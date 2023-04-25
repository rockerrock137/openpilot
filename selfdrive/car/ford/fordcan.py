from common.numpy_fast import clip
from common.conversions import Conversions as CV
from cereal import car

GearShifter = car.CarState.GearShifter

def fordchecksum(cnt, speed):
  # Checksum is 255 - cnt - speed - df (data qualifier, 3 signals VALID data) with bitwise shifting and rounding on the speed.
  speed = int(round(speed / 0.01, 2))
  top = speed >> 8
  bottom = speed & 0xff
  cs = 255 - cnt - top - bottom - 3
  if cs < 0:
    cs = cs + 255
  return cs

def spam_cancel_button(packer):
  values = {
    "Cancel": 1
  }
  return packer.make_can_msg("Steering_Buttons", 0, values)

def ParkAid_Data(packer, enabled, apply_steer, sappControlState, standstill):
  # sappState 1 = Off, 2 = On | sappControl 0 = No request, 1 = Request
  # No angle request at standstill because it causes sporadic steering wheel drift.
  if sappControlState in [1, 2]:
    sappState = 2
    sappControl = 0
    if enabled and not standstill:
      sappControl = 1
  else:
    sappState = 1
    sappControl = 0

  values = {
    "ApaSys_D_Stat": sappState,
    "EPASExtAngleStatReq": sappControl,
    "ExtSteeringAngleReq2": apply_steer,
  }
  return packer.make_can_msg("ParkAid_Data", 2, values)

def EngVehicleSpThrottle2(packer, frame, speed, gearShifter):
  # If in reverse, send appropriate data
  if gearShifter == GearShifter.reverse:
    reverse = 3
    trailer = 1
  else:
    reverse = 1
    trailer = 0

  cnt = frame % 16
  cs = fordchecksum(cnt, speed)

  values = {
    "VehVTrlrAid_B_Avail": trailer,
    "VehVActlEng_No_Cs": cs,
    "VehVActlEng_No_Cnt": cnt,
    "VehVActlEng_D_Qf": 3,
    "Veh_V_ActlEng": speed,
    "GearRvrse_D_Actl": reverse,
  }
  return packer.make_can_msg("EngVehicleSpThrottle2", 2, values)

def BrakeSysFeatures(packer, frame, speed):
  cnt = frame % 16
  cs = fordchecksum(cnt, speed)

  values = {
    "LsmcBrkDecel_D_Stat": 4,
    "VehVActlBrk_No_Cs": cs,
    "Veh_V_ActlBrk": speed,
    "VehVActlBrk_No_Cnt": cnt,
    "VehVActlBrk_D_Qf": 3,
  }
  return packer.make_can_msg("BrakeSysFeatures", 2, values)
