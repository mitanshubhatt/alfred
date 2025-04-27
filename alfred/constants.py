from enum import Enum


class ResetPeriod(Enum, str):
    HOURLY = "hourly"
    DAILY = "daily"
    MONTHLY = "monthly"
