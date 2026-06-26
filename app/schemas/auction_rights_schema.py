from pydantic import BaseModel


class AuctionRightsCreate(BaseModel):

    auction_id: int

    base_right: str

    tenant_priority: str

    lease_deposit: float = 0

    takeover_amount: float = 0

    occupancy: str

    eviction_level: str

    comment: str = ""


class AuctionRightsUpdate(BaseModel):

    base_right: str

    tenant_priority: str

    lease_deposit: float

    takeover_amount: float

    occupancy: str

    eviction_level: str

    comment: str

