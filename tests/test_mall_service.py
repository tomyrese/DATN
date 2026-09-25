import pytest
import os
import tempfile
from src.services.mall_service import MallService

def test_mall_service_db_and_queue():
    with tempfile.TemporaryDirectory() as tmpdir:
        db_path = os.path.join(tmpdir, "test_mall.db")
        mall = MallService(db_path=db_path)

        # 1. Create first order
        order1 = mall.create_delivery_order(
            creator_name="Quầy A",
            pickup_poi_id="poi_highlands",
            dropoff_poi_id="poi_reception",
            item_description="2 ly Cafe"
        )
        assert order1.order_id is not None
        assert order1.status == "MOVING_TO_PICKUP"
        assert mall.active_order_id == order1.order_id

        # 2. Create second order while first is running -> should go to PENDING queue
        order2 = mall.create_delivery_order(
            creator_name="Quầy B",
            pickup_poi_id="poi_uniqlo",
            dropoff_poi_id="poi_warehouse",
            item_description="Kiện quần áo"
        )
        assert order2.status == "PENDING"
        assert mall.active_order_id == order1.order_id

        # 3. Update order 1 through phases
        mall.update_order_status(order1.order_id, "ARRIVED_AT_PICKUP", 100)
        active = mall.get_active_order()
        assert active.status == "ARRIVED_AT_PICKUP"

        mall.update_order_status(order1.order_id, "DELIVERING", 0)
        active = mall.get_active_order()
        assert active.status == "DELIVERING"

        mall.update_order_status(order1.order_id, "ARRIVED_AT_DROPOFF", 100)
        active = mall.get_active_order()
        assert active.status == "ARRIVED_AT_DROPOFF"

        # 4. Complete order 1 -> should auto-dispatch order 2 from queue to MOVING_TO_PICKUP
        mall.update_order_status(order1.order_id, "COMPLETED", 100)
        assert mall.active_order_id == order2.order_id

        active2 = mall.get_active_order()
        assert active2.order_id == order2.order_id
        assert active2.status == "MOVING_TO_PICKUP"
