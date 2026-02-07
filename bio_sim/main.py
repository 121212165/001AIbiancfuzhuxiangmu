"""
生物模拟平台 - 主入口
"""
import sys
import os

# 添加项目路径到 Python 路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from visualizers.pygame_visualizer import run_boids, run_ecosystem, run_game_of_life, run_genetic_algorithm


def main():
    """主函数 - 选择要运行的模拟"""
    print("=" * 50)
    print("生物模拟平台")
    print("=" * 50)
    print("\n请选择要运行的模拟：")
    print("1. Boids群体行为模拟（鸟群/鱼群）")
    print("2. 生态系统模拟（捕食者-猎物）")
    print("3. 康威生命游戏（细胞自动机）")
    print("4. 遗传算法进化模拟")
    print("0. 退出")

    choice = input("\n请输入选项（0-4）: ").strip()

    if choice == '1':
        print("\n启动Boids模拟...")
        print("操作说明：空格-暂停/继续，R-重置，ESC-退出")
        run_boids()
    elif choice == '2':
        print("\n启动生态系统模拟...")
        print("操作说明：空格-暂停/继续，R-重置，ESC-退出")
        run_ecosystem()
    elif choice == '3':
        print("\n启动生命游戏...")
        print("操作说明：空格-暂停/继续，R-重置，ESC-退出")
        run_game_of_life()
    elif choice == '4':
        print("\n启动遗传算法模拟...")
        print("操作说明：空格-暂停/继续，R-重置，ESC-退出")
        run_genetic_algorithm()
    elif choice == '0':
        print("再见！")
        sys.exit(0)
    else:
        print("无效选项，请重新运行程序")
        sys.exit(1)


if __name__ == '__main__':
    main()
