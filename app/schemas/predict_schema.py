from pydantic import BaseModel, Field, model_validator


class IrisRequest(BaseModel):
    sepal_length: float = Field(..., gt=0, description="cm")
    sepal_width:  float = Field(..., gt=0, description="cm")
    petal_length: float = Field(..., gt=0, description="cm")
    petal_width:  float = Field(..., gt=0, description="cm")

    @model_validator(mode="after")
    def check_ranges(self):
        if not (0.5 <= self.sepal_length <= 10 and 0.5 <= self.petal_length <= 10):
            raise ValueError("lengths look out of range (0.5–10 cm)")
        if not (0.1 <= self.sepal_width <= 10 and 0.1 <= self.petal_width <= 10):
            raise ValueError("widths look out of range (0.1–10 cm)")
        return self


class IrisResponse(BaseModel):
    predicted_class: str
    class_index: int
    confidence: float
    probabilities: dict[str, float]


class IrisBatchRequest(BaseModel):
    """Batch prediction request."""

    items: list[IrisRequest]


class IrisBatchResponse(BaseModel):
    """Batch prediction response."""

    items: list[IrisResponse]
    count: int
