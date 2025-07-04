import math
from langchain.tools import tool
from typing import Dict


@tool
def head_end_area(bore_dia_in: float) -> dict:
    """Calculate the head end area of a compressor cylinder from bore diameter.

    Args:
        bore_dia_in (float): Bore diameter in inches.

    Returns:
        float: Head end area in square inches.

    Raises:
        ValueError: If bore diameter is non-positive or invalid.
    """
    if not isinstance(bore_dia_in, (int, float)):
        raise ValueError("Bore diameter must be a valid number")
    if bore_dia_in <= 0:
        raise ValueError("Bore diameter must be positive")
    he_area = (math.pi / 4) * (bore_dia_in**2)
    return {"head_end_area": he_area}


@tool
def crank_end_area(bore_dia_in: float, rod_dia_in: float) -> float:
    """Calculate the crank end area from bore diameter and rod diameter.

    Args:
        bore_dia_in (float): Bore diameter in inches.
        rod_dia_in (float): Rod diameter in inches.

    Returns:
        float: Crank end area in square inches.

    Raises:
        ValueError: If bore or rod diameter is non-positive, invalid, or rod diameter >= bore diameter.
    """
    if not all(isinstance(x, (int, float)) for x in [bore_dia_in, rod_dia_in]):
        raise ValueError("Bore and rod diameters must be valid numbers")
    if bore_dia_in <= 0 or rod_dia_in <= 0:
        raise ValueError("Bore and rod diameters must be positive")
    if rod_dia_in >= bore_dia_in:
        raise ValueError("Rod diameter must be less than bore diameter")
    ce_area = (math.pi / 4) * (bore_dia_in**2 - rod_dia_in**2)
    return {"crank_end_area": ce_area}


@tool
def head_end_displacement(head_end_area: float, stroke_in: float) -> float:
    """Calculate head end displacement from head end area and stroke length.

    Args:
        head_end_area (float): Head end area in square inches.
        stroke_in (float): Stroke length in inches.

    Returns:
        head_end_displacement_value (float): Head end displacement in cubic inches.

    Raises:
        ValueError: If area or stroke is non-positive or invalid.
    """

    if not all(isinstance(x, (int, float)) for x in [head_end_area, stroke_in]):
        raise ValueError("Area and stroke must be valid numbers")
    if head_end_area <= 0 or stroke_in <= 0:
        raise ValueError("Area and stroke must be positive")

    head_end_displacement_value = head_end_area * stroke_in
    return {"head_end_displacement_value": head_end_displacement_value}


@tool
def crank_end_displacement(crank_end_area: float, stroke_in: float) -> float:
    """Calculate crank end displacement from crank end area and stroke length.

    Args:
        crank_end_area (float): Crank end area in square inches.
        stroke_in (float): Stroke length in inches.

    Returns:
        crank_end_displacement_value (float): Crank end displacement in cubic inches.

    Raises:
        ValueError: If area or stroke is non-positive or invalid.
    """

    if not all(isinstance(x, (int, float)) for x in [crank_end_area, stroke_in]):
        raise ValueError("Area and stroke must be valid numbers")
    if crank_end_area <= 0 or stroke_in <= 0:
        raise ValueError("Area and stroke must be positive")

    crank_end_displacement_value = crank_end_area * stroke_in
    return {"crank_end_displacement_value": crank_end_displacement_value}


@tool
def swept_volume(
    head_end_displacement_value: float, crank_end_displacement_value: float
) -> float:
    """Calculate swept volume from head end and crank end displacement values.

    Args:
        head_end_displacement_value (float): Head end displacement in cubic inches.
        crank_end_displacement_value (float): Crank end displacement in cubic inches.

    Returns:
        swept_volume_in3 (float): Swept volume in a cylinder in cubic inches.

    Raises:
        ValueError: If displacements are non-positive or invalid.
    """

    if not all(
        isinstance(x, (int, float))
        for x in [head_end_displacement_value, crank_end_displacement_value]
    ):
        raise ValueError("Displacements must be valid numbers")
    if head_end_displacement_value <= 0 or crank_end_displacement_value <= 0:
        raise ValueError("Displacements must be positive")
    swept_volume_in3 = head_end_displacement_value + crank_end_displacement_value
    return {"swept_volume_in3": swept_volume_in3}


@tool
def head_end_clearances(
    head_end_displacement_value: float,
    head_end_fixed_clearance_pct: float,
    head_end_added_clearance_pct: float,
) -> Dict[str, float]:
    """Calculate head end clearances from head end displacement value and head end fixed clearance percentage and head end added clearance percentage.

    Args:
        head_end_displacement_value (float): Head end displacement in cubic inches.
        head_end_fixed_clearance_pct (float): Head end Fixed clearance percentage.
        head_end_added_clearance_pct (float): Head end Added clearance percentage.

    Returns:
        dict: Dictionary with head end fixed clearance, head end added clearance (in cubic inches), and head end total clearance percentage.

    Raises:
        ValueError: If displacement is non-positive, clearances are negative, or inputs are invalid.
    """

    if not all(
        isinstance(x, (int, float))
        for x in [
            head_end_displacement_value,
            head_end_fixed_clearance_pct,
            head_end_added_clearance_pct,
        ]
    ):
        raise ValueError("Input values must be valid numbers")
    if head_end_displacement_value <= 0:
        raise ValueError("Displacement must be positive")
    if head_end_fixed_clearance_pct < 0 or head_end_added_clearance_pct < 0:
        raise ValueError("Clearances must be non-negative")
    fixed_clearance = (head_end_fixed_clearance_pct / 100) * head_end_displacement_value
    added_clearance = (head_end_added_clearance_pct / 100) * head_end_displacement_value
    total_clearance_pct = head_end_fixed_clearance_pct + head_end_added_clearance_pct

    return {
        "head_end_fixed_clearance_in3": fixed_clearance,
        "head_end_added_clearance_in3": added_clearance,
        "head_end_total_clearance_pct": total_clearance_pct,
    }


@tool
def crank_end_clearances(
    crank_end_displacement_value: float,
    crank_end_fixed_clearance_pct: float,
    crank_end_added_clearance_pct: float,
) -> Dict[str, float]:
    """Calculate crank end clearances from crank end displacement value and crank end fixed clearance percentage and crank end added clearance percentage.

    Args:
        crank_end_displacement_value (float): Crank end displacement in cubic inches.
        crank_end_fixed_clearance_pct (float): Crank end Fixed clearance percentage.
        crank_end_added_clearance_pct (float): Crank end Added clearance percentage.

    Returns:
        dict: Dictionary with crank end fixed clearance, crank end added clearance (in cubic inches), and crank end total clearance percentage.

    Raises:
        ValueError: If displacement is non-positive, clearances are negative, or inputs are invalid.
    """

    if not all(
        isinstance(x, (int, float))
        for x in [
            crank_end_displacement_value,
            crank_end_fixed_clearance_pct,
            crank_end_added_clearance_pct,
        ]
    ):
        raise ValueError("Input values must be valid numbers")
    if crank_end_displacement_value <= 0:
        raise ValueError("Displacement must be positive")
    if crank_end_fixed_clearance_pct < 0 or crank_end_added_clearance_pct < 0:
        raise ValueError("Clearances must be non-negative")
    fixed_clearance = (
        crank_end_fixed_clearance_pct / 100
    ) * crank_end_displacement_value
    added_clearance = (
        crank_end_added_clearance_pct / 100
    ) * crank_end_displacement_value
    total_clearance_pct = crank_end_fixed_clearance_pct + crank_end_added_clearance_pct

    return {
        "crank_end_fixed_clearance_in3": fixed_clearance,
        "crank_end_added_clearance_in3": added_clearance,
        "crank_end_total_clearance_pct": total_clearance_pct,
    }


@tool
def mean_piston_speed(stroke_in: float, rpm: float) -> float:
    """Calculate mean piston speed in ft/min from stroke length and RPM.

    Args:
        stroke_in (float): Stroke length in inches.
        rpm (float): Revolutions per minute.

    Returns:
        float: Mean piston speed in feet per minute.

    Raises:
        ValueError: If stroke or RPM is non-positive or invalid.
    """
    if not all(isinstance(x, (int, float)) for x in [stroke_in, rpm]):
        raise ValueError("Stroke and RPM must be valid numbers")
    if stroke_in <= 0 or rpm <= 0:
        raise ValueError("Stroke and RPM must be positive")
    mean_piston_speed_ft_min = (stroke_in * rpm) / 12

    return {"mean_piston_speed_ft_min": mean_piston_speed_ft_min}


@tool
def he_suction_valve_diameter(
    bore_dia_in: float,
    mean_piston_speed_ft_min: float,
    suction_gas_velocity_ft_min: float,
    he_suction_valve_quantity: float,
) -> float:
    """Calculate head end suction valve diameter.

    Args:
        bore_dia_in (float): Bore diameter in inches.
        mean_piston_speed_ft_min (float): Mean piston speed in feet per minute.
        suction_gas_velocity_ft_min (float): Suction gas velocity in feet per minute.
        he_suction_valve_quantity (float): Number of suction valves in head end.

    Returns:
        float: Head end suction valve diameter in inches.

    Raises:
        ValueError: If inputs are non-positive, invalid, or gas velocity is zero.
    """

    if not all(
        isinstance(x, (int, float))
        for x in [
            bore_dia_in,
            mean_piston_speed_ft_min,
            suction_gas_velocity_ft_min,
            he_suction_valve_quantity,
        ]
    ):
        raise ValueError("Input values must be valid numbers")
    if (
        bore_dia_in <= 0
        or mean_piston_speed_ft_min <= 0
        or he_suction_valve_quantity <= 0
    ):
        raise ValueError(
            "Bore diameter, piston speed, and valve quantity must be positive"
        )
    if suction_gas_velocity_ft_min <= 0:
        raise ValueError("Suction gas velocity must be positive")
    bore_dia_ft = bore_dia_in / 12
    diameter_ft = math.sqrt(
        (bore_dia_ft**2)
        * mean_piston_speed_ft_min
        / (he_suction_valve_quantity * suction_gas_velocity_ft_min)
    )
    he_suc_valve_dia = diameter_ft * 12

    return {"head_end_suction_valve_diameter_in": he_suc_valve_dia}


@tool
def he_discharge_valve_diameter(
    bore_dia_in: float,
    mean_piston_speed_ft_min: float,
    discharge_gas_velocity_ft_min: float,
    he_discharge_valve_quantity: float,
) -> float:
    """Calculate head end discharge valve diameter.

    Args:
        bore_dia_in (float): Bore diameter in inches.
        mean_piston_speed_ft_min (float): Mean piston speed in feet per minute.
        discharge_gas_velocity_ft_min (float): Discharge gas velocity in feet per minute.
        he_discharge_valve_quantity (float): Number of discharge valves in head end.

    Returns:
        float: Head end discharge valve diameter in inches.

    Raises:
        ValueError: If inputs are non-positive, invalid, or gas velocity is zero.
    """
    if not all(
        isinstance(x, (int, float))
        for x in [
            bore_dia_in,
            mean_piston_speed_ft_min,
            discharge_gas_velocity_ft_min,
            he_discharge_valve_quantity,
        ]
    ):
        raise ValueError("Input values must be valid numbers")
    if (
        bore_dia_in <= 0
        or mean_piston_speed_ft_min <= 0
        or he_discharge_valve_quantity <= 0
    ):
        raise ValueError(
            "Bore diameter, piston speed, and valve quantity must be positive"
        )
    if discharge_gas_velocity_ft_min <= 0:
        raise ValueError("Discharge gas velocity must be positive")
    bore_dia_ft = bore_dia_in / 12
    diameter_ft = math.sqrt(
        (bore_dia_ft**2)
        * mean_piston_speed_ft_min
        / (he_discharge_valve_quantity * discharge_gas_velocity_ft_min)
    )
    he_dis_valve_dia = diameter_ft * 12
    return {"head_end_discharge_valve_diameter_in": he_dis_valve_dia}


@tool
def ce_suction_valve_diameter(
    bore_dia_in: float,
    mean_piston_speed_ft_min: float,
    suction_gas_velocity_ft_min: float,
    ce_suction_valve_quantity: float,
) -> float:
    """Calculate crank end suction valve diameter.

    Args:
        bore_dia_in (float): Bore diameter in inches.
        mean_piston_speed_ft_min (float): Mean piston speed in feet per minute.
        suction_gas_velocity_ft_min (float): Suction gas velocity in feet per minute.
        ce_suction_valve_quantity (float): Number of suction valves in crank end.

    Returns:
        float: Crank end suction valve diameter in inches.

    Raises:
        ValueError: If inputs are non-positive, invalid, or gas velocity is zero.
    """
    if not all(
        isinstance(x, (int, float))
        for x in [
            bore_dia_in,
            mean_piston_speed_ft_min,
            suction_gas_velocity_ft_min,
            ce_suction_valve_quantity,
        ]
    ):
        raise ValueError("Input values must be valid numbers")
    if (
        bore_dia_in <= 0
        or mean_piston_speed_ft_min <= 0
        or ce_suction_valve_quantity <= 0
    ):
        raise ValueError(
            "Bore diameter, piston speed, and valve quantity must be positive"
        )
    if suction_gas_velocity_ft_min <= 0:
        raise ValueError("Suction gas velocity must be positive")
    bore_dia_ft = bore_dia_in / 12
    diameter_ft = math.sqrt(
        (bore_dia_ft**2)
        * mean_piston_speed_ft_min
        / (ce_suction_valve_quantity * suction_gas_velocity_ft_min)
    )
    ce_suc_valve_dia = diameter_ft * 12
    return {"crank_end_suction_valve_diameter_in": ce_suc_valve_dia}


@tool
def ce_discharge_valve_diameter(
    bore_dia_in: float,
    mean_piston_speed_ft_min: float,
    discharge_gas_velocity_ft_min: float,
    ce_discharge_valve_quantity: float,
) -> float:
    """Calculate crank end discharge valve diameter.

    Args:
        bore_dia_in (float): Bore diameter in inches.
        mean_piston_speed_ft_min (float): Mean piston speed in feet per minute.
        discharge_gas_velocity_ft_min (float): Discharge gas velocity in feet per minute.
        ce_discharge_valve_quantity (float): Number of discharge valves in crank end.

    Returns:
        float: Crank end discharge valve diameter in inches.

    Raises:
        ValueError: If inputs are non-positive, invalid, or gas velocity is zero.
    """
    if not all(
        isinstance(x, (int, float))
        for x in [
            bore_dia_in,
            mean_piston_speed_ft_min,
            discharge_gas_velocity_ft_min,
            ce_discharge_valve_quantity,
        ]
    ):
        raise ValueError("Input values must be valid numbers")
    if (
        bore_dia_in <= 0
        or mean_piston_speed_ft_min <= 0
        or ce_discharge_valve_quantity <= 0
    ):
        raise ValueError(
            "Bore diameter, piston speed, and valve quantity must be positive"
        )
    if discharge_gas_velocity_ft_min <= 0:
        raise ValueError("Discharge gas velocity must be positive")
    bore_dia_ft = bore_dia_in / 12
    diameter_ft = math.sqrt(
        (bore_dia_ft**2)
        * mean_piston_speed_ft_min
        / (ce_discharge_valve_quantity * discharge_gas_velocity_ft_min)
    )

    ce_dis_valve_dia = diameter_ft * 12
    return {"crank_end_discharge_valve_diameter_in": ce_dis_valve_dia}
