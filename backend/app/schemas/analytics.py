from pydantic import BaseModel, ConfigDict
from typing import List, Dict, Any, Optional
from decimal import Decimal


class VehicleRepairStats(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    model: str
    repair_count: int
    average_cost: Decimal


class CostTrendPoint(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    period: str
    labor_cost: Decimal
    material_cost: Decimal
    service_cost: Decimal
    total_cost: Decimal


class NegativeFeedbackCase(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    feedback_id: int
    rating: Optional[int]
    feedback_comment: str
    order_id: int
    order_number: str
    worker_id: int
    worker_name: str


class WorkerTaskDistribution(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    skill_type: str
    task_count: int
    percentage: float


class UnfinishedOrderStats(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    status: str
    count: int


class ComprehensiveAnalyticsResponse(BaseModel):
    vehicle_repair_stats: List[VehicleRepairStats]
    cost_trends: List[CostTrendPoint]
    negative_feedback_cases: List[NegativeFeedbackCase]
    worker_task_distribution: List[WorkerTaskDistribution]
    unfinished_order_stats: List[UnfinishedOrderStats] 