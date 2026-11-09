from openpilot.cereal import log
from openpilot.common.constants import CV
from openpilot.common.realtime import DT_MDL

LaneChangeState = log.LaneChangeState
LaneChangeDirection = log.LaneChangeDirection

LANE_CHANGE_SPEED_MIN = 20 * CV.MPH_TO_MS
LANE_CHANGE_TIME_MAX = 10.
LANE_CHANGE_START_TIME = 0.5

# Nudgeless lane change (BYD Atto 3 fork). The turn signal alone starts the change,
# no steering-wheel nudge needed. Guards:
#  - one automatic change per blinker activation; holding the stalk does not chain
#    changes. A second change needs blinker off/on, or a manual nudge.
#  - blind spot blocks the change; once a blind-spot hit is seen, the zone must stay
#    clear for AUTO_LANE_CHANGE_BSM_CLEAR_TIME before the change starts.
#  - pressing the brake cancels the pending automatic change for this activation.
AUTO_LANE_CHANGE = True
AUTO_LANE_CHANGE_BSM_CLEAR_TIME = 1.0  # s

class DesireHelper:
  def __init__(self):
    self.lane_change_state = LaneChangeState.off
    self.lane_change_direction = LaneChangeDirection.none
    self.lane_change_timer = 0.0
    self.prev_one_blinker = False
    self.desire = log.Desire.none
    self.auto_lane_change_armed = False
    self.bsm_clear_timer = 0.0
    self.bsm_seen = False
    self.prev_raw_one_blinker = False

  @staticmethod
  def get_lane_change_direction(CS):
    return LaneChangeDirection.left if CS.leftBlinker else LaneChangeDirection.right

  def update(self, carstate, lateral_active, lane_change_prob):
    v_ego = carstate.vEgo
    one_blinker = carstate.leftBlinker != carstate.rightBlinker
    below_lane_change_speed = v_ego < LANE_CHANGE_SPEED_MIN

    if not lateral_active or self.lane_change_timer > LANE_CHANGE_TIME_MAX:
      self.lane_change_state = LaneChangeState.off
      self.lane_change_direction = LaneChangeDirection.none
      self.lane_change_timer = 0.0
    else:
      if self.lane_change_state == LaneChangeState.off and one_blinker and not self.prev_one_blinker and not below_lane_change_speed:
        self.lane_change_state = LaneChangeState.preLaneChange
        self.lane_change_timer = 0.0
        # Initialize lane change direction to prevent UI alert flicker
        self.lane_change_direction = self.get_lane_change_direction(carstate)
        # Arm one automatic change only on a real stalk activation, not when
        # engaging with the blinker already on
        self.auto_lane_change_armed = AUTO_LANE_CHANGE and not self.prev_raw_one_blinker
        self.bsm_seen = False
        self.bsm_clear_timer = 0.0

      elif self.lane_change_state == LaneChangeState.preLaneChange:
        # Update lane change direction
        self.lane_change_direction = self.get_lane_change_direction(carstate)

        torque_applied = carstate.steeringPressed and \
                         ((carstate.steeringTorque > 0 and self.lane_change_direction == LaneChangeDirection.left) or
                          (carstate.steeringTorque < 0 and self.lane_change_direction == LaneChangeDirection.right))

        blindspot_detected = ((carstate.leftBlindspot and self.lane_change_direction == LaneChangeDirection.left) or
                              (carstate.rightBlindspot and self.lane_change_direction == LaneChangeDirection.right))

        if blindspot_detected:
          self.bsm_seen = True
          self.bsm_clear_timer = 0.0
        else:
          self.bsm_clear_timer += DT_MDL

        if carstate.brakePressed:
          self.auto_lane_change_armed = False

        bsm_settled = not self.bsm_seen or self.bsm_clear_timer >= AUTO_LANE_CHANGE_BSM_CLEAR_TIME
        auto_start = self.auto_lane_change_armed and bsm_settled

        if not one_blinker or below_lane_change_speed:
          self.lane_change_state = LaneChangeState.off
          self.lane_change_direction = LaneChangeDirection.none
          self.lane_change_timer = 0.0
        elif (torque_applied or auto_start) and not blindspot_detected:
          self.lane_change_state = LaneChangeState.laneChangeStarting
          self.lane_change_timer = 0.0
          self.auto_lane_change_armed = False

      elif self.lane_change_state == LaneChangeState.laneChangeStarting:
        self.lane_change_timer += DT_MDL

        if lane_change_prob < 0.02 and self.lane_change_timer >= LANE_CHANGE_START_TIME:
          self.lane_change_timer = 0.0
          if one_blinker:
            self.lane_change_state = LaneChangeState.preLaneChange
            self.lane_change_direction = self.get_lane_change_direction(carstate)
          else:
            self.lane_change_state = LaneChangeState.off
            self.lane_change_direction = LaneChangeDirection.none

    self.prev_one_blinker = one_blinker and lateral_active
    self.prev_raw_one_blinker = one_blinker

    self.desire = log.Desire.none
    if self.lane_change_state == LaneChangeState.laneChangeStarting:
      if self.lane_change_direction == LaneChangeDirection.left:
        self.desire = log.Desire.laneChangeLeft
      elif self.lane_change_direction == LaneChangeDirection.right:
        self.desire = log.Desire.laneChangeRight
