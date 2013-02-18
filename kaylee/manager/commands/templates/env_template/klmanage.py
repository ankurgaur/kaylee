#!/usr/bin/env python
import os

def main():
    from kaylee.manager import LocalCommandsManager
    LocalCommandsManager.execute_from_command_line()

if __name__ == '__main__':
    main()
