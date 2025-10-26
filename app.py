import streamlit as st
from modules.app import ReSocialApp

def main():
    """
    主应用函数
    初始化应用并管理页面路由
    """
    app = ReSocialApp()
    app.run()

if __name__ == "__main__":
    main()
