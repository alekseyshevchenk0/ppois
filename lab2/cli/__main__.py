from cli.app import Console, MenuApp
from cli.demo_data import build_demo_state


def main() -> None:
    MenuApp(build_demo_state(), Console()).run()


if __name__ == "__main__":
    main()
