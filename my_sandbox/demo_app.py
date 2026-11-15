# -*- coding: utf-8 -*-
"""
ملف تجربة معزول لاختبار التعديل الجراحي
"""

def calculate_discount(price, customer_type):
    # نوع العميل: VIP يحصل على 20% خصم، Normal يحصل على 5% خصم
    if customer_type == "VIP":
        return price * 0.80
    elif customer_type == "Normal":
        return price * 0.95
    return price

def get_server_status():
    # كود ناقص يحتاج إكمال
    status = {"server": "online", "database": "connected", "latency_ms": 25}
    return status

if __name__ == "__main__":
    print("Testing discount VIP:", calculate_discount(100, "VIP"))
    print("Testing discount Normal:", calculate_discount(100, "Normal"))
