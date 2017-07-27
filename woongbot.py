from slacker import Slacker

token = 'xoxb-217774856690-LjuvF3LuUTJQQUmUzL2L6xkd'
slack = Slacker(token)


attachments_dict = dict()
attachments_dict['prtext'] = "계속 업데이트 중.."
attachments_dict['fallback'] = "Hi★ Woong Bot is Coming!!"
attachments_dict['title'] = "다른 텍스트 보다 크고 볼드되어서 보이는 title"
# attachments_dict['title_link'] = "https://corikachu.github.io"
# attachments_dict['text'] = "본문 텍스트! 5줄이 넘어가면 *show more*로 보이게 됩니다."
# attachments_dict['mrkdwn_in'] = ["text", "pretext"]  # 마크다운을 적용시킬 인자들을 선택합니다.

attachments = [attachments_dict]

slack.chat.post_message(channel="#woong_bot", text=None, attachments=attachments, as_user=True)
