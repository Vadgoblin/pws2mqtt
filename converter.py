from typing import Optional


class WeatherUnits:
    # ---------------------------------------------------------------------------
    # Imperial -> Metric (SI canonical: °C, hPa, km/h, mm)
    # ---------------------------------------------------------------------------

    @staticmethod
    def f_to_c(f: Optional[float]) -> Optional[float]:
        return (f - 32.0) * (5.0 / 9.0) if f is not None else None

    @staticmethod
    def inhg_to_hpa(inhg: Optional[float]) -> Optional[float]:
        return inhg * 33.863886666667 if inhg is not None else None

    @staticmethod
    def mph_to_kmh(mph: Optional[float]) -> Optional[float]:
        return mph * 1.609344 if mph is not None else None

    @staticmethod
    def in_to_mm(inches: Optional[float]) -> Optional[float]:
        return inches * 25.4 if inches is not None else None

    # ---------------------------------------------------------------------------
    # Metric -> Imperial
    # ---------------------------------------------------------------------------

    @staticmethod
    def c_to_f(c: Optional[float]) -> Optional[float]:
        return (c * (9.0 / 5.0)) + 32.0 if c is not None else None

    @staticmethod
    def hpa_to_inhg(hpa: Optional[float]) -> Optional[float]:
        return hpa / 33.863886666667 if hpa is not None else None

    @staticmethod
    def kmh_to_mph(kmh: Optional[float]) -> Optional[float]:
        return kmh / 1.609344 if kmh is not None else None

    @staticmethod
    def mm_to_in(mm: Optional[float]) -> Optional[float]:
        return mm / 25.4 if mm is not None else None