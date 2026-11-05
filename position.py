"""
Returns the UR3 cup pose for one card.
Input:  player (1 to 4), hand (1 or 2, 2 = split hand), card (1 to 7)
Output: [x, y, z, rx, ry, rz] in the robot base frame, metres and radians
"""

import numpy as np
from scipy.spatial.transform import Rotation as R

# Reference pose: player 1, hand 2, card 1 (cup TCP, pendant mm converted to m)
REF_POSE = [0.44763, 0.01592, -0.02127, 0.254, -3.152, 0.0]

SEAT_STEP = 20.0    # deg between players
HAND_ANGLE = 8.0    # deg between hand 1 and hand 2
SEAT_DIR = -1       # direction from player 1 toward player 4
R_MAX = 0.5443      # m, radius of the last card (max reach)
Z_STEP = 0.0005     # m height added per card
MAX_FAN = 7         # cards fanned before stacking on the last spot

_REF_POS = np.array(REF_POSE[:3])
_REF_ROT = R.from_rotvec(REF_POSE[3:])
_R_REF = float(np.hypot(_REF_POS[0], _REF_POS[1]))
_RADIAL = np.array([_REF_POS[0], _REF_POS[1], 0.0]) / _R_REF
FAN_STEP = (R_MAX - _R_REF) / (MAX_FAN - 1)


def card_position(player, hand, card):
    """Cup pose [x, y, z, rx, ry, rz] for one card."""
    if not 1 <= player <= 4:
        raise ValueError(f"Player must be 1 to 4, got {player}")
    if not 1 <= hand <= 2:
        raise ValueError(f"Hand must be 1 or 2, got {hand}")
    if card < 1:
        raise ValueError(f"Card must be 1 or higher, got {card}")

    n_fan = min(card - 1, MAX_FAN - 1)
    pos = _REF_POS + n_fan * FAN_STEP * _RADIAL + np.array([0.0, 0.0, (card - 1) * Z_STEP])

    delta = SEAT_DIR * ((player - 1) * SEAT_STEP - (2 - hand) * HAND_ANGLE)
    rz = R.from_euler("z", delta, degrees=True)

    return [float(v) for v in (*rz.apply(pos), *(rz * _REF_ROT).as_rotvec())]

import matplotlib.pyplot as plt


def plot(pose):
    """Plot the x, y position of a pose returned by card_position."""
    x_mm = pose[0] * 1000
    y_mm = pose[1] * 1000

    plt.figure(figsize=(8, 8))
    plt.plot(0, 0, "ks", markersize=8, label="Robotbase")
    plt.plot(
        x_mm,
        y_mm,
        label=f"TCP ({x_mm:.1f}, {y_mm:.1f}) mm",
        color="blue",
        marker="o",
        markersize=6,
    )

    t = np.linspace(0, 2 * np.pi, 300)  # 300 angles around the full circle
    r_mm = R_MAX * 1000  # max reach in mm (R_MAX is in m)
    plt.plot(r_mm * np.cos(t), r_mm * np.sin(t),  # x = r cos t, y = r sin t
             "--", color="grey",
             label=f"Maks rekkevidde {r_mm:.0f} mm")

    plt.axis("equal")
    plt.xlabel("x(mm)")
    plt.ylabel("y(mm)")
    plt.title("TCP posisjon")
    plt.grid(True)
    plt.legend(loc="upper right")
    plt.show()
    plt.savefig("tcp_position.png", dpi=300)

if __name__ == "__main__":
    # Manual test: type the numbers and get the pose back
    player = int(input("Player nr (1 to 4): "))
    hand = int(input("Hand nr (1 or 2): "))
    card = int(input("Card nr (1 to 7): "))
    pose = card_position(player, hand, card)
    plot(pose)
    print("Pose (m, rad):", [round(v, 5) for v in pose])
    print("Pendant (mm):", [round(v * 1000, 2) for v in pose[:3]], [round(v, 4) for v in pose[3:]])
