from datetime import datetime
from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field
from decimal import Decimal
from .base import BaseCreate

class FinancialReportSyncResponse(BaseCreate):
    """Schema para sincronização de relatórios financeiros"""
    report_type: str = Field(..., description="Tipo do relatório: 'daily' ou 'range'")
    period_start: Optional[datetime] = Field(None, description="Data de início do período")
    period_end: Optional[datetime] = Field(None, description="Data de fim do período")
    
    # Métricas principais
    total_sales: int = Field(0, description="Número total de vendas")
    total_revenue: float = Field(0.0, description="Receita total")
    gross_profit: float = Field(0.0, description="Lucro bruto")
    net_profit: float = Field(0.0, description="Lucro líquido")
    gross_margin: float = Field(0.0, description="Margem bruta (%)")
    net_margin: float = Field(0.0, description="Margem líquida (%)")
    average_ticket: float = Field(0.0, description="Ticket médio")
    total_expenses: float = Field(0.0, description="Total de despesas")
    
    # Métricas detalhadas
    expenses_detail: Dict[str, float] = Field(
        default_factory=dict,
        description="Detalhamento das despesas"
    )
    
    sales_by_user: Dict[str, Dict[str, Any]] = Field(
        default_factory=dict,
        description="Vendas por usuário"
    )
    
    top_products: List[Dict[str, Any]] = Field(
        default_factory=list,
        description="Top 5 produtos mais vendidos"
    )
    
    category_metrics: Dict[str, Dict[str, Any]] = Field(
        default_factory=dict,
        description="Métricas por categoria de produto"
    )
    
    payment_metrics: Dict[str, Dict[str, Any]] = Field(
        default_factory=dict,
        description="Métricas por método de pagamento"
    )
    
    performance_analysis: Dict[str, Dict[str, Any]] = Field(
        default_factory=dict,
        description="Análise de desempenho"
    )
    
    daily_metrics: Optional[Dict[str, Dict[str, Any]]] = Field(
        None,
        description="Métricas diárias (apenas para relatórios de período)"
    )
    
    # Informações de contexto
    generated_at: datetime = Field(..., description="Data/hora de geração do relatório")
    generated_by: str = Field(..., description="Usuário que gerou o relatório")
    
    class Config:
        from_attributes = True
        json_encoders = {
            Decimal: lambda v: float(v) if v is not None else 0.0
        }

class ReportSyncRequest(BaseModel):
    """Request para sincronização de relatórios"""
    reports: List[FinancialReportSyncResponse] = Field(..., description="Lista de relatórios para sincronizar")
    last_sync: datetime = Field(..., description="Última data de sincronização")

class ReportSyncResponse(BaseModel):
    """Resposta da sincronização de relatórios"""
    synced_reports: List[FinancialReportSyncResponse] = Field(
        default_factory=list,
        description="Relatórios sincronizados com sucesso"
    )
    
    conflicts: List[FinancialReportSyncResponse] = Field(
        default_factory=list,
        description="Relatórios com conflitos de versão"
    )
    
    server_updated: List[FinancialReportSyncResponse] = Field(
        default_factory=list,
        description="Relatórios atualizados no servidor"
    )
    
    class Config:
        from_attributes = True