from copy import copy

import numpy as np
import matplotlib.pyplot as plt
from scipy import linalg as LA
from scipy.sparse import linalg as las

from opentorsion.disk_element import Disk
from opentorsion.shaft_element import Shaft
from opentorsion.gear_element import Gear
from opentorsion.induction_motor import Induction_motor
from opentorsion.assembly import Assembly
from opentorsion.plots import Plots


"""Example cases"""


def ex_1(get_assembly=False):
    """
    Two disks connected with a shaft.
    Eigenfrequencies and a campbell diagram.
    """
    shafts, disks = [], []

    Ip = 400  # Disk inertia (kgm²)
    L = 2.5e3  # Shaft length (mm)
    D = 0.2e3  # Shaft outer diameter (mm)

    node = 0
    disks.append(Disk(node, Ip))
    shafts.append(Shaft(node, node + 1, L, D))
    node += 1
    disks.append(Disk(node, Ip))

    assembly = Assembly(shaft_elements=shafts, disk_elements=disks)

    if get_assembly:
        return assembly
    else:
        # Print the eigenfrequencies of the powertrain
        o_d, eigenfrequencies, d_r = assembly.modal_analysis()
        print(eigenfrequencies.round(3))

        # Campbell diagram
        plot_tools = Plots(assembly)
        plot_tools.campbell_diagram(frequency_range=10)

        return print("Example 1 finished")


def ex_2(get_assembly=False):
    """Powertrain with shafts, disks and gears"""
    # Induction motor inertia
    J_IM = 0.196  # kgm^2
    # Synchronous reluctance motor inertia
    J_SRM = 0.575  # kgm^2
    # Gear inertia
    Ig = 0.007  # kgm^2

    # Inertias
    J_hub1 = 17e-3  # kgm^2
    J_hub2 = 17e-3  # kgm^2
    J_tube = 37e-3 * (0.55 - 2 * 0.128)  # kgm^2
    J_coupling = J_hub1 + J_hub2 + J_tube  # kgm^2
    # Stiffnesses
    K_insert1 = 41300  # Nm/rad
    K_insert2 = 41300  # Nm/rad
    K_tube = 389000 * (0.55 - 2 * 0.128)  # Nm/rad
    K_coupling = 1 / (1 / K_insert1 + 1 / K_tube)  # Nm/rad

    shafts, disks, gears = [], [], []

    rho = 7850  # Material density
    G = 81e9  # Shear modulus

    disks.append(Disk(0, J_IM))  # Motor represented as a mass
    shafts.append(Shaft(0, 1, None, None, k=40050, I=0.045))  # Coupling
    gears.append(gear1 := Gear(1, Ig, 1))  # Gear
    gears.append(Gear(2, Ig, -1.95, parent=gear1))  # Gear

    shafts.append(Shaft(2, 3, None, None, k=40050, I=0.045))  # Coupling

    # Roll with varying diameters
    shafts.append(Shaft(3, 4, 185, 100))
    shafts.append(Shaft(4, 5, 335, 119))
    shafts.append(Shaft(5, 6, 72, 125))
    shafts.append(Shaft(6, 7, 150, 320))
    shafts.append(Shaft(7, 8, 3600, 320, idl=287))
    shafts.append(Shaft(8, 9, 150, 320))
    shafts.append(Shaft(9, 10, 72, 125))
    shafts.append(Shaft(10, 11, 335, 119))
    shafts.append(Shaft(11, 12, 185, 100))
    ##

    shafts.append(Shaft(11, 12, None, None, k=180e3, I=15e-4))  # Torque transducer
    shafts.append(Shaft(12, 13, None, None, k=40050, I=0.045))  # Coupling
    disks.append(Disk(13, J_SRM))  # Motor represented as a mass

    assembly = Assembly(shaft_elements=shafts, disk_elements=disks, gear_elements=gears)

    if get_assembly:
        return assembly
    else:
        plot_tools = Plots(assembly)
        plot_tools.figure_2D()  # A 2D representation of the powertrain
        plot_tools.figure_eigenmodes()  # Plot the eigenmodes of the powertrain

        return print("Example 2 finished")


def ex_3(linear_parameters=True, noload=True):
    """Induction motor and two disks connected with a shaft"""
    if noload:
        if linear_parameters:
            parameters_nonlinear = (
                np.array([23.457, 19.480, 30.470, 30.030, 28.904]) * 1e-3
            )
            parameters_linear = (
                np.array([23.486, 18.900, 13.119, 12.981, 11.963]) * 1e-3
            )
        else:
            parameters_nonlinear = (
                np.array([23.457, 19.480, 30.470, 30.030, 28.904]) * 1e-3
            )
            parameters_linear = (
                np.array([23.457, 19.480, 30.470, 30.030, 28.904]) * 1e-3
            )

    else:
        if linear_parameters:
            parameters_nonlinear = (
                np.array([24.492, 19.450, 29.386, 29.004, 27.921]) * 1e-3
            )
            parameters_linear = (
                np.array([23.342, 18.668, 12.686, 12.507, 11.579]) * 1e-3
            )

        else:
            parameters_nonlinear = (
                np.array([24.492, 19.450, 29.386, 29.004, 27.921]) * 1e-3
            )
            parameters_linear = (
                np.array([24.492, 19.450, 29.386, 29.004, 27.921]) * 1e-3
            )

    f = 60
    p = 4
    speed = 895.3
    voltage = 4000
    motor_holopainen = Induction_motor(
        0,
        speed,
        f,
        p,
        voltage=voltage,
        small_signal=True,
        circuit_parameters_nonlinear=parameters_nonlinear,
        circuit_parameters_linear=parameters_linear,
    )

    shafts = [Shaft(0, 1, 0, 0, k=9.775e6)]
    disks = [Disk(0, 211.4), Disk(1, 8.3)]
    assembly = Assembly(shafts, disk_elements=disks, motor_elements=[motor_holopainen])

    damped, freqs, ratios = assembly.modal_analysis()

    for f in damped / (np.pi * 2):
        print(f)

    return print("Example 3 finished")


def ex_4():  # incomplete
    """
    Planetary gear:
    Input shaft attached to sun gear and ring gear, output shaft attached to carrier and planet gears.

    Three cases:
    1. Ring gear stationary, sun and carrier moving. Output speed positive.
    2. Sun gear stationary, ring and carrier moving. Output speed 2. > 1.
    3. Carrier stationary, sun and ring moving. Output speed negative.
    """

    pgs = 5  # number of planet gears
    gears = []
    case = 0

    if case == 0:

        sun_gear = Gear(n, I=0, R=6)
        gears.append(sun_gear)
        n += 1

        planet_gear = Gear(n, I=0, R=3, parent=sun_gear)
        gears.append(planet_gear)
        n += 1

        ring_gear = Gear(n, I=0, R=9, parent=planet_gear)
        gears.append(ring_gear)

        print("node:", n, "gears:", gears)

    if case == 1:

        sun_gear = Gear(n, I=0, R=56)
        gears.append(sun_gear)
        n += 1

        carrier = Gear(n, I=0, R=95)  # R_c = R_s + R_p
        gears.append(carrier)
        n += 1

        for i in range(pgs):
            planet_gear = Gear(n, I=0, R=39, parent=sun_gear, parent2=carrier)
            gears.append(planet_gear)
            n += 1
        n -= 1

        print("carrier node:", carrier.node, "gears:", gears)

    if case == 2:

        ring_gear = Gear(n, I=0, R=12)
        gears.append(ring_gear)
        n += 1

        carrier = Gear(n, I=0, R=9)  # R_c = R_s + R_p
        gears.append(carrier)
        n += 1

        for i in range(pgs):
            planet_gear = Gear(n, I=0, R=-3, parent=carrier, parent2=ring_gear)
            gears.append(planet_gear)
            n += 1
        n -= 1

        print("carrier node:", carrier.node, "gears:", gears)

    if case == 3:

        sun_gear = Gear(n, I=0, R=56)
        gears.append(sun_gear)
        n += 1

        ring_gear = Gear(n + pgs, I=0, R=134)
        gears.append(ring_gear)
        # n += 1

        for i in range(pgs):
            planet_gear = Gear(n, I=0, R=39, parent=sun_gear, parent2=ring_gear)
            gears.append(planet_gear)
            n += 1
        # n -= 1

        gears.pop(1)
        ring_gear = Gear(n, I=0, R=134, parent=sun_gear)
        gears.append(ring_gear)

    return print("Example 4 finished")


def ex_5():
    """Time-domain analysis of a powertrain"""

    nstep = 300

    # random signal generation

    a_range = [0, 2]
    a = (
        np.random.rand(nstep) * (a_range[1] - a_range[0]) + a_range[0]
    )  # range for amplitude

    b_range = [2, 10]
    b = (
        np.random.rand(nstep) * (b_range[1] - b_range[0]) + b_range[0]
    )  # range for frequency
    b = np.round(b)
    b = b.astype(int)

    b[0] = 0

    for i in range(1, np.size(b)):
        b[i] = b[i - 1] + b[i]

    # Random Signal
    i = 0
    random_signal = np.zeros(nstep)
    while b[i] < np.size(random_signal):
        k = b[i]
        random_signal[k:] = a[i]
        i = i + 1

    # PRBS
    a = np.zeros(nstep)
    j = 0
    while j < nstep:
        a[j] = 5
        a[j + 1] = -5
        j = j + 2

    i = 0
    prbs = np.zeros(nstep)
    while b[i] < np.size(prbs):
        k = b[i]
        prbs[k:] = -a[i]
        i = i + 1

    assembly = ex_2(get_assembly=True)  # The powertrain from example 2
    t_in = np.linspace(0, 299, 300)  # timesteps for time-domain analysis
    # u1 = np.linspace(-5, -20, 300) # input vector
    tout, torque, speed, angle = assembly.time_domain(t_in, u1=random_signal, u2=prbs)
    torque = np.array(torque)

    plt.figure("opentorsion-torque")
    plt.plot(tout, torque)
    plt.grid(alpha=0.3)
    plt.xlabel("t")

    plt.figure(0)
    plt.subplot(2, 1, 1)
    plt.plot(random_signal, drawstyle="steps", label="Random Signal")
    plt.legend()
    plt.subplot(2, 1, 2)
    plt.plot(prbs, drawstyle="steps", label="PRBS")
    plt.legend()
    plt.show()
    return print("Example 5 finished")


if __name__ == "__main__":
    print("openTorsion examples.\nChoose a number (1-5)")
    choice = input()
    if choice == "1":
        ex_1()
    if choice == "2":
        ex_2()
    if choice == "3":
        ex_3()
    if choice == "4":
        ex_4()
    if choice == "5":
        ex_5()
    else:
        print("Choice invalid: quitting.")
