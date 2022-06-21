from colorama import Fore, Style, Back

def greeter():
    version = "v2022.06"
    titleText = f"< MetroBuild {version} by D.V. >"
    print(f"{Style.BRIGHT}{Back.LIGHTBLUE_EX} {titleText} {Style.RESET_ALL}")