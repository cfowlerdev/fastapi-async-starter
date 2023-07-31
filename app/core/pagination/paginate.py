from pydantic import BaseModel
from .schemas import PageParams, PagedResponse, T

def paginate(page_params: PageParams, query, ResponseSchema: BaseModel) -> PagedResponse[T]:
    paginated_query = query.offset((page_params.page - 1) * page_params.size).limit(page_params.size).all()
    return PagedResponse(
        total = query.count(),
        page = page_params.page,
        size = page_params.size,
        results = [ResponseSchema.model_validate(item) for item in paginated_query]
    )
