import appbuilder
import os
import re

# 请前往千帆AppBuilder官网创建密钥，流程详见：https://cloud.baidu.com/doc/AppBuilder/s/Olq6grrt6#1%E3%80%81%E5%88%9B%E5%BB%BA%E5%AF%86%E9%92%A5
# 设置环境变量
os.environ["APPBUILDER_TOKEN"] = 'bce-v3/ALTAK-eh4pLo8laymbjz6VkHpAf/0a09449916ea91c7ee9d34af4b2ef238121d51ce'
app_id = '4885c346-800e-4492-bc65-f507289d55e8'  # 已发布AppBuilder应用ID，可在console端查看
# 初始化智能体
builder = appbuilder.AppBuilderClient(app_id)
# 创建会话
conversation_id = builder.create_conversation()
# 运行对话
out = builder.run(conversation_id, "提出三个关于个人的简短的有趣的可以用一句话回答的问题")
# 打印会话结果 
print(out.content.answer)

# Parse the result into 3 strings
text = out.content.answer
# Use regex to find answers after each question number
answers = re.findall(r'\d\.\s(.+?)(?=\s*\d\.|\s*$)', text, re.DOTALL)

# Remove extra whitespace
answers = [answer.strip() for answer in answers]

# Store the answers in variables
answer1 = answers[0]
answer2 = answers[1]
answer3 = answers[2]

# Print the variables to confirm
print("\nParsed Answers:")
print(answer1)
print(answer2)
print(answer3)