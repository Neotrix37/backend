import logging
from fastapi import APIRouter, HTTPException, status, Depends, Query
from typing import List, Any, Optional
from sqlalchemy.orm import Session, joinedload
from datetime import datetime, date, timedelta
from decimal import Decimal

from app.core.database import get_db
from app.core.security import get_current_active_user
from app.models.user import User
from app.models.sale import Sale
from app.models.sale_item import SaleItem
from app.models.product import Product
from app.models.category import Category

router = APIRouter()
logger = logging.getLogger(__name__)

@router.get("/financial/daily")
async def get_daily_financial_report(
    report_date: date = Query(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
) -> Any:
    """Relatório financeiro diário com vendas, receitas, métricas por categoria, métodos de pagamento,
    top produtos vendidos e análise de desempenho."""
    try:
        # Buscar vendas do dia com items e usuário
        sales = db.query(Sale).options(
            joinedload(Sale.items).joinedload(SaleItem.product).joinedload(Product.category),
            joinedload(Sale.user)
        ).filter(
            Sale.created_at >= report_date,
            Sale.created_at < report_date.replace(day=report_date.day + 1),
            Sale.status == "CONCLUIDA"
        ).all()
        
        total_sales = len(sales)
        total_revenue = sum(sale.total_amount for sale in sales if sale.total_amount)
        
        # Calcular lucro bruto
        gross_profit = 0
        for sale in sales:
            for item in sale.items:
                cost_price = item.product.preco_compra if item.product else 0
                gross_profit += (item.unit_price - cost_price) * item.quantity
        
        # Calcular despesas (exemplo fixo para demonstração)
        total_expenses = Decimal('3000.00')  # MT 3,000.00 de despesas (salários)
        
        # Calcular lucro líquido
        net_profit = gross_profit - total_expenses
        
        # Calcular margens
        gross_margin = (gross_profit / total_revenue * 100) if total_revenue > 0 else 0
        net_margin = (net_profit / total_revenue * 100) if total_revenue > 0 else 0
        
        # Ticket médio
        average_ticket = total_revenue / total_sales if total_sales > 0 else 0
        
        # Vendas por usuário
        sales_by_user = {}
        for sale in sales:
            user_name = sale.user.full_name if sale.user else "Usuário Desconhecido"
            if user_name not in sales_by_user:
                sales_by_user[user_name] = {"revenue": 0, "sales_count": 0}
            sales_by_user[user_name]["revenue"] += sale.total_amount or 0
            sales_by_user[user_name]["sales_count"] += 1
        
        # Top 5 produtos mais vendidos
        product_sales = {}
        for sale in sales:
            for item in sale.items:
                product_name = item.product.nome if item.product else "Produto Desconhecido"
                if product_name not in product_sales:
                    product_sales[product_name] = {"quantity": 0, "revenue": 0}
                product_sales[product_name]["quantity"] += item.quantity or 0
                product_sales[product_name]["revenue"] += item.unit_price * item.quantity if item.unit_price else 0
        
        # Ordenar por quantidade vendida e pegar top 5
        top_products = sorted(
            [{"name": k, "quantity": v["quantity"], "revenue": v["revenue"]} 
             for k, v in product_sales.items()],
            key=lambda x: x["quantity"],
            reverse=True
        )[:5]
        
        # Métricas por categoria
        category_metrics = {}
        for sale in sales:
            for item in sale.items:
                category_name = item.product.category.name if item.product and item.product.category else "Sem Categoria"
                if category_name not in category_metrics:
                    category_metrics[category_name] = {"revenue": 0, "quantity": 0}
                category_metrics[category_name]["revenue"] += item.unit_price * item.quantity if item.unit_price else 0
                category_metrics[category_name]["quantity"] += item.quantity or 0
        
        # Métricas por método de pagamento
        payment_metrics = {}
        for sale in sales:
            payment_method = sale.payment_method or "Desconhecido"
            if payment_method not in payment_metrics:
                payment_metrics[payment_method] = {"revenue": 0, "count": 0}
            payment_metrics[payment_method]["revenue"] += sale.total_amount or 0
            payment_metrics[payment_method]["count"] += 1
        
        # Análise de desempenho
        performance_analysis = {
            "gross_margin": {
                "status": "CRÍTICO" if gross_margin == 0 else "NORMAL",
                "analysis": "Margem bruta baixa (0.0%). Urgente revisar preços e custos." if gross_margin == 0 
                            else f"Margem bruta: {gross_margin:.1f}%"
            },
            "net_profit": {
                "status": "CRÍTICO" if net_profit < 0 else "POSITIVO",
                "analysis": "Prejuízo no período. Necessária ação imediata para reverter resultado." if net_profit < 0
                            else f"Lucro líquido positivo: MT {net_profit:,.2f}"
            },
            "expenses": {
                "status": "POSITIVO" if total_expenses == 0 else "NORMAL",
                "analysis": "Boa gestão de despesas (0.0% das vendas)" if total_expenses == 0
                            else f"Despesas: MT {total_expenses:,.2f} ({total_expenses/total_revenue*100:.1f}% das vendas)" if total_revenue > 0
                            else f"Despesas: MT {total_expenses:,.2f} (sem vendas para calcular porcentagem)"
            }
        }
        
        return {
            "date": report_date.isoformat(),
            "total_sales": total_sales,
            "total_revenue": float(total_revenue) if total_revenue else 0.0,
            "gross_profit": float(gross_profit),
            "net_profit": float(net_profit),
            "gross_margin": gross_margin,
            "net_margin": net_margin,
            "average_ticket": float(average_ticket),
            "total_expenses": total_expenses,
            "expenses_detail": {
                "Salários Funcionários": 3000.00
            },
            "sales_by_user": sales_by_user,
            "top_products": top_products,
            "category_metrics": category_metrics,
            "payment_metrics": payment_metrics,
            "performance_analysis": performance_analysis,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error generating daily financial report: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred while generating the financial report."
        )

@router.get("/financial/range")
async def get_financial_report_range(
    start_date: date = Query(...),
    end_date: date = Query(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
) -> Any:
    """Relatório financeiro para um período específico com análise completa"""
    try:
        # Buscar vendas no período com items e usuário
        sales = db.query(Sale).options(
            joinedload(Sale.items).joinedload(SaleItem.product).joinedload(Product.category),
            joinedload(Sale.user)
        ).filter(
            Sale.created_at >= start_date,
            Sale.created_at <= end_date.replace(day=end_date.day + 1),
            Sale.status == "CONCLUIDA"
        ).all()
        
        total_sales = len(sales)
        total_revenue = sum(sale.total_amount for sale in sales if sale.total_amount)
        
        # Calcular lucro bruto
        gross_profit = 0
        for sale in sales:
            for item in sale.items:
                cost_price = item.product.preco_compra if item.product else 0
                gross_profit += (item.unit_price - cost_price) * item.quantity
        
        # Calcular despesas (exemplo fixo para demonstração)
        total_expenses = Decimal('3000.00')  # MT 3,000.00 de despesas (salários)
        
        # Calcular lucro líquido
        net_profit = gross_profit - total_expenses
        
        # Calcular margens
        gross_margin = (gross_profit / total_revenue * 100) if total_revenue > 0 else 0
        net_margin = (net_profit / total_revenue * 100) if total_revenue > 0 else 0
        
        # Ticket médio
        average_ticket = total_revenue / total_sales if total_sales > 0 else 0
        
        # Vendas por usuário
        sales_by_user = {}
        for sale in sales:
            user_name = sale.user.full_name if sale.user else "Usuário Desconhecido"
            if user_name not in sales_by_user:
                sales_by_user[user_name] = {"revenue": 0, "sales_count": 0}
            sales_by_user[user_name]["revenue"] += sale.total_amount or 0
            sales_by_user[user_name]["sales_count"] += 1
        
        # Top 5 produtos mais vendidos
        product_sales = {}
        for sale in sales:
            for item in sale.items:
                product_name = item.product.nome if item.product else "Produto Desconhecido"
                if product_name not in product_sales:
                    product_sales[product_name] = {"quantity": 0, "revenue": 0}
                product_sales[product_name]["quantity"] += item.quantity or 0
                product_sales[product_name]["revenue"] += item.unit_price * item.quantity if item.unit_price else 0
        
        # Ordenar por quantidade vendida e pegar top 5
        top_products = sorted(
            [{"name": k, "quantity": v["quantity"], "revenue": v["revenue"]} 
             for k, v in product_sales.items()],
            key=lambda x: x["quantity"],
            reverse=True
        )[:5]
        
        # Métricas por categoria
        category_metrics = {}
        for sale in sales:
            for item in sale.items:
                category_name = item.product.category.name if item.product and item.product.category else "Sem Categoria"
                if category_name not in category_metrics:
                    category_metrics[category_name] = {"revenue": 0, "quantity": 0}
                category_metrics[category_name]["revenue"] += item.unit_price * item.quantity if item.unit_price else 0
                category_metrics[category_name]["quantity"] += item.quantity or 0
        
        # Métricas por método de pagamento
        payment_metrics = {}
        for sale in sales:
            payment_method = sale.payment_method or "Desconhecido"
            if payment_method not in payment_metrics:
                payment_metrics[payment_method] = {"revenue": 0, "count": 0}
            payment_metrics[payment_method]["revenue"] += sale.total_amount or 0
            payment_metrics[payment_method]["count"] += 1
        
        # Análise de desempenho
        performance_analysis = {
            "gross_margin": {
                "status": "CRÍTICO" if gross_margin == 0 else "NORMAL",
                "analysis": "Margem bruta baixa (0.0%). Urgente revisar preços e custos." if gross_margin == 0 
                            else f"Margem bruta: {gross_margin:.1f}%"
            },
            "net_profit": {
                "status": "CRÍTICO" if net_profit < 0 else "POSITIVO",
                "analysis": "Prejuízo no período. Necessária ação imediata para reverter resultado." if net_profit < 0
                            else f"Lucro líquido positivo: MT {net_profit:,.2f}"
            },
            "expenses": {
                "status": "POSITIVO" if total_expenses == 0 else "NORMAL",
                "analysis": "Boa gestão de despesas (0.0% das vendas)" if total_expenses == 0
                            else f"Despesas: MT {total_expenses:,.2f} ({total_expenses/total_revenue*100:.1f}% das vendas)" if total_revenue > 0
                            else f"Despesas: MT {total_expenses:,.2f} (sem vendas para calcular porcentagem)"
            }
        }
        
        # Métricas diárias
        daily_metrics = {}
        current_date = start_date
        while current_date <= end_date:
            daily_sales = [s for s in sales if s.created_at.date() == current_date]
            daily_revenue = sum(s.total_amount for s in daily_sales if s.total_amount)
            
            daily_metrics[current_date.isoformat()] = {
                "sales_count": len(daily_sales),
                "total_revenue": float(daily_revenue) if daily_revenue else 0.0,
                "average_sale_value": float(daily_revenue / len(daily_sales)) if daily_sales else 0.0
            }
            current_date = current_date + timedelta(days=1)
        
        return {
            "period": {
                "start_date": start_date.isoformat(),
                "end_date": end_date.isoformat()
            },
            "total_sales": total_sales,
            "total_revenue": float(total_revenue) if total_revenue else 0.0,
            "gross_profit": float(gross_profit),
            "net_profit": float(net_profit),
            "gross_margin": gross_margin,
            "net_margin": net_margin,
            "average_ticket": float(average_ticket),
            "total_expenses": total_expenses,
            "expenses_detail": {
                "Salários Funcionários": 3000.00
            },
            "sales_by_user": sales_by_user,
            "top_products": top_products,
            "category_metrics": category_metrics,
            "payment_metrics": payment_metrics,
            "performance_analysis": performance_analysis,
            "daily_metrics": daily_metrics,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error generating financial report range: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred while generating the financial report."
        )