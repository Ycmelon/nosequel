from PyInquirer import style_from_dict, Token

# Replace these and save as "config.py"
db_user = "cli-user"
db_password = ""
connection_string = (
    f"mongodb+srv://{db_user}:{db_password}@etc.mongodb.net/etc?retryWrites=true&w=majority"
)

style = style_from_dict(
    {
        Token.QuestionMark: "#E91E63 bold",
        Token.Selected: "#673AB7 bold",
        Token.Instruction: "",  # default
        Token.Answer: "#2196f3 bold",
        Token.Question: "",
    }
)
