from db import Operator


def main():
    operator = Operator()
    operator.create_db()
    operator.fill_data()


if __name__ == '__main__':
    main()