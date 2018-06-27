# -*- coding: utf-8 -*-

import sys
import logging
import time


def main():
    FORMAT = "%(asctime)s - %(message)s"
    logging.basicConfig(format=FORMAT)
    logging.getLogger().setLevel("INFO".upper())

    if len(sys.argv) < 2:
        opts = []
        return
    else:
        pass
    

    # step 1: import item data
    if sys.argv[1] == "import_items":
        from ubskin_web_django.common import import_item_data
        import_item_data.import_item_data()
    # export 「微客推广订单」
    # elif sys.argv[1] == "export_weike_orders":
    #     import app.workers.order_worker as order_worker
    #     order_worker.export_weike_orders()
    

    else:
        print("No command to do.")


if __name__ == "__main__":
    main()
