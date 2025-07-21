import argparse
import clr
import os
import sys
import time

# 設定DLL路徑
dll_dir = os.path.abspath('.')
sys.path.append(dll_dir)
clr.AddReference('Mitsubishi_FX5U')
from Equipment import Mitsubishi_FX5U

# 允許誤差（角度到達的容忍範圍）
ANGLE_TOLERANCE = 0.1

def wait_until_reach(getter, target, desc):
    while True:
        current = getter()
        print(f"{desc} current: {current}")
        if abs(current - target) <= ANGLE_TOLERANCE:
            print(f"{desc} reached: {current}")
            break

def main():
    parser = argparse.ArgumentParser(description="Mitsubishi FX5U 控制工具")
    parser.add_argument('--port', type=str, default='COM10', help="COM port (default: COM10)")
    subparsers = parser.add_subparsers(dest='command', required=True)

    # set-theta
    parser_theta = subparsers.add_parser('set-theta', help="設定 theta 角度")
    parser_theta.add_argument('angle', type=float, help="目標 theta 角度")

    # set-phi
    parser_phi = subparsers.add_parser('set-phi', help="設定 phi 角度")
    parser_phi.add_argument('angle', type=float, help="目標 phi 角度")

    # set-both
    parser_both = subparsers.add_parser('set-both', help="同時設定 theta 與 phi 角度")
    parser_both.add_argument('theta', type=float, help="目標 theta 角度")
    parser_both.add_argument('phi', type=float, help="目標 phi 角度")

    # read-theta
    subparsers.add_parser('read-theta', help="讀取 theta 角度")

    # read-phi
    subparsers.add_parser('read-phi', help="讀取 phi 角度")

    args = parser.parse_args()

    fx5u = Mitsubishi_FX5U(args.port)

    if args.command == 'set-theta':
        fx5u.SetThetaAngle(args.angle)
        wait_until_reach(fx5u.ReadThetaPosition, args.angle, "Theta")

    elif args.command == 'set-phi':
        fx5u.SetPhiAngle(args.angle)
        wait_until_reach(fx5u.ReadPhiPosition, args.angle, "Phi")

    elif args.command == 'set-both':
        fx5u.SetThetaAngle(args.theta)
        fx5u.SetPhiAngle(args.phi)
        # 等待兩個角度都到達
        while True:
            theta_now = fx5u.ReadThetaPosition()
            phi_now = fx5u.ReadPhiPosition()
            print(f"Theta current: {theta_now}, Phi current: {phi_now}")
            if (abs(theta_now - args.theta) <= ANGLE_TOLERANCE and
                abs(phi_now - args.phi) <= ANGLE_TOLERANCE):
                print(f"Theta reached: {theta_now}, Phi reached: {phi_now}")
                break

    elif args.command == 'read-theta':
        theta_now = fx5u.ReadThetaPosition()
        print(theta_now)

    elif args.command == 'read-phi':
        phi_now = fx5u.ReadPhiPosition()
        print(phi_now)

if __name__ == '__main__':
    main()
