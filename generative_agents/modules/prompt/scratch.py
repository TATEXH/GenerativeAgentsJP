"""generative_agents.prompt.scratch"""

import random
import datetime
import re
from string import Template

from modules import utils
from modules.memory import Event
from modules.model import parse_llm_output


class Scratch:
    def __init__(self, name, currently, config):
        self.name = name
        self.currently = currently
        self.config = config
        self.template_path = "data/prompts"

    def build_prompt(self, template, data):
        with open(f"{self.template_path}/{template}.txt", "r", encoding="utf-8") as file:
            file_content = file.read()

        template = Template(file_content)
        filled_content = template.substitute(data)

        return filled_content

    def _base_desc(self):
        return self.build_prompt(
            "base_desc",
            {
                "name": self.name,
                "age": self.config["age"],
                "innate": self.config["innate"],
                "learned": self.config["learned"],
                "lifestyle": self.config["lifestyle"],
                "daily_plan": self.config["daily_plan"],
                "date": utils.get_timer().daily_format_cn(),
                "currently": self.currently,
            }
        )

    def prompt_poignancy_event(self, event):
        prompt = self.build_prompt(
            "poignancy_event",
            {
                "base_desc": self._base_desc(),
                "agent": self.name,
                "event": event.get_describe(),
            }
        )

        def _callback(response):
            pattern = [
                "評価[:： ]+(\d{1,2})",
                "(\d{1,2})",
            ]
            return int(parse_llm_output(response, pattern, "match_last"))

        return {
            "prompt": prompt,
            "callback": _callback,
            "failsafe": random.choice(list(range(10))) + 1,
        }

    def prompt_poignancy_chat(self, event):
        prompt = self.build_prompt(
            "poignancy_chat",
            {
                "base_desc": self._base_desc(),
                "agent": self.name,
                "event": event.get_describe(),
            }
        )

        def _callback(response):
            pattern = [
                "評価[:： ]+(\d{1,2})",
                "(\d{1,2})",
            ]
            return int(parse_llm_output(response, pattern, "match_last"))

        return {
            "prompt": prompt,
            "callback": _callback,
            "failsafe": random.choice(list(range(10))) + 1,
        }

    def prompt_wake_up(self):
        prompt = self.build_prompt(
            "wake_up",
            {
                "base_desc": self._base_desc(),
                "lifestyle": self.config["lifestyle"],
                "agent": self.name,
            }
        )

        def _callback(response):
            patterns = [
                "(\d{1,2}):00",
                "(\d{1,2})",
                "\d{1,2}",
            ]
            wake_up_time = int(parse_llm_output(response, patterns))
            if wake_up_time > 11:
                wake_up_time = 11
            return wake_up_time

        return {"prompt": prompt, "callback": _callback, "failsafe": 6}

    def prompt_schedule_init(self, wake_up):
        prompt = self.build_prompt(
            "schedule_init",
            {
                "base_desc": self._base_desc(),
                "lifestyle": self.config["lifestyle"],
                "agent": self.name,
                "wake_up": wake_up,
            }
        )

        def _callback(response):
            patterns = [
                "\d{1,2}\. (.*)。",
                "\d{1,2}\. (.*)",
                "\d{1,2}\) (.*)。",
                "\d{1,2}\) (.*)",
                "(.*)。",
                "(.*)",
            ]
            return parse_llm_output(response, patterns, mode="match_all")

        failsafe = [
            "朝6時に起床し朝食の準備をする",
            "朝7時に朝食を食べる",
            "朝8時に読書をする",
            "昼12時に昼食を食べる",
            "午後1時に少し昼寝をする",
            "夜7時にリラックスしてテレビを見る",
            "夜11時に就寝する",
        ]
        return {"prompt": prompt, "callback": _callback, "failsafe": failsafe}

    def prompt_schedule_daily(self, wake_up, daily_schedule):
        hourly_schedule = ""
        for i in range(wake_up):
            hourly_schedule += f"[{i}:00] 睡眠\n"
        for i in range(wake_up, 24):
            hourly_schedule += f"[{i}:00] <活動>\n"

        prompt = self.build_prompt(
            "schedule_daily",
            {
                "base_desc": self._base_desc(),
                "agent": self.name,
                "daily_schedule": "；".join(daily_schedule),
                "hourly_schedule": hourly_schedule,
            }
        )

        failsafe = {
            "6:00": "起床し朝の日課を行う",
            "7:00": "朝食を食べる",
            "8:00": "読書をする",
            "9:00": "読書をする",
            "10:00": "読書をする",
            "11:00": "読書をする",
            "12:00": "昼食を食べる",
            "13:00": "少し昼寝をする",
            "14:00": "少し昼寝をする",
            "15:00": "少し昼寝をする",
            "16:00": "作業を続ける",
            "17:00": "作業を続ける",
            "18:00": "帰宅する",
            "19:00": "リラックスしてテレビを見る",
            "20:00": "リラックスしてテレビを見る",
            "21:00": "就寝前の読書",
            "22:00": "就寝の準備",
            "23:00": "就寝する",
        }

        def _callback(response):
            patterns = [
                "\[(\d{1,2}:\d{2})\] " + self.name + "(.*)。",
                "\[(\d{1,2}:\d{2})\] " + self.name + "(.*)",
                "\[(\d{1,2}:\d{2})\] " + "(.*)。",
                "\[(\d{1,2}:\d{2})\] " + "(.*)",
            ]
            outputs = parse_llm_output(response, patterns, mode="match_all")
            assert len(outputs) >= 5, "less than 5 schedules"
            return {s[0]: s[1] for s in outputs}

        return {"prompt": prompt, "callback": _callback, "failsafe": failsafe}

    def prompt_schedule_decompose(self, plan, schedule):
        def _plan_des(plan):
            start, end = schedule.plan_stamps(plan, time_format="%H:%M")
            return f'{start} から {end}まで、{self.name} は {plan["describe"]} を計画している'

        indices = range(
            max(plan["idx"] - 1, 0), min(plan["idx"] + 2, len(schedule.daily_schedule))
        )

        start, end = schedule.plan_stamps(plan, time_format="%H:%M")
        increment = max(int(plan["duration"] / 100) * 5, 5)

        prompt = self.build_prompt(
            "schedule_decompose",
            {
                "base_desc": self._base_desc(),
                "agent": self.name,
                "plan": "；".join([_plan_des(schedule.daily_schedule[i]) for i in indices]),
                "increment": increment,
                "start": start,
                "end": end,
            }
        )

        def _callback(response):
            import re
            
            # 複数のパターンを順番に試行
            patterns = [
                # パターン1: 「予定」あり、全角括弧
                r"(\d{1,2})\)\s*[^:：]*[:：]\s*(.*?)\s*予定（所要時間：(\d{1,2})分?、残り：\d*分?）",
                # パターン2: 「予定」なし、全角括弧（実際のLLM出力に対応）
                r"(\d{1,2})\)\s*[^:：]*[:：]\s*(.*?)（所要時間：(\d{1,2})分?、残り：\d*分?）",
                # パターン3: 「予定」あり、半角括弧
                r"(\d{1,2})\)\s*[^:：]*[:：]\s*(.*?)\s*予定\(所要時間[：:]\s*(\d{1,2})分?、残り[：:]\s*\d*分?\)",
                # パターン4: 「予定」なし、半角括弧
                r"(\d{1,2})\)\s*[^:：]*[:：]\s*(.*?)\(所要時間[：:]\s*(\d{1,2})分?、残り[：:]\s*\d*分?\)",
                # パターン5: より柔軟なパターン（全角・半角混在対応）
                r"(\d{1,2})\)[^:：]*[:：]([^（(]*)(?:予定)?[（(]所要時間[:：]\s*(\d+)",
            ]
            
            schedules = None
            matched_pattern = None
            
            # 各パターンを試行
            for i, pattern in enumerate(patterns):
                try:
                    matches = re.findall(pattern, response)
                    if matches:
                        schedules = matches
                        matched_pattern = i + 1
                        print(f"[DEBUG] Matched with pattern {matched_pattern}")
                        break
                except Exception as e:
                    continue
            
            # どのパターンにもマッチしない場合
            if not schedules:
                print(f"[DEBUG] No pattern matched. Response sample: {response[:200]}")
                # 最も基本的なパターンで再試行
                fallback_pattern = r"(\d{1,2})\)[^:：]*[:：]([^（(）)]*)"
                matches = re.findall(fallback_pattern, response)
                if matches:
                    # 時間情報がない場合はデフォルト10分を使用
                    schedules = [(m[0], m[1].strip(), "10") for m in matches]
                    print(f"[DEBUG] Used fallback pattern")
                else:
                    raise Exception("Failed to parse any schedule format")
            
            # 結果を整形
            result_schedules = []
            for s in schedules:
                if len(s) >= 3:
                    # 通常のパターンマッチ結果
                    result_schedules.append((s[1].strip(".。 "), int(s[2])))
                elif len(s) == 3 and isinstance(s[2], str):
                    # fallbackパターンの結果
                    result_schedules.append((s[1].strip(".。 "), int(s[2])))
                    
            # 残り時間の調整
            total_used = sum([s[1] for s in result_schedules])
            left = plan["duration"] - total_used
            if left > 0:
                result_schedules.append((plan["describe"], left))
                
            return result_schedules

        failsafe = [(plan["describe"], 10) for _ in range(int(plan["duration"] / 10))]
        return {"prompt": prompt, "callback": _callback, "failsafe": failsafe}

    def prompt_schedule_revise(self, action, schedule):
        plan, _ = schedule.current_plan()
        start, end = schedule.plan_stamps(plan, time_format="%H:%M")
        act_start_minutes = utils.daily_duration(action.start)
        original_plan, new_plan = [], []

        def _plan_des(start, end, describe):
            if not isinstance(start, str):
                start = start.strftime("%H:%M")
            if not isinstance(end, str):
                end = end.strftime("%H:%M")
            return "[{} 至 {}] {}".format(start, end, describe)

        for de_plan in plan["decompose"]:
            de_start, de_end = schedule.plan_stamps(de_plan, time_format="%H:%M")
            original_plan.append(_plan_des(de_start, de_end, de_plan["describe"]))
            if de_plan["start"] + de_plan["duration"] <= act_start_minutes:
                new_plan.append(_plan_des(de_start, de_end, de_plan["describe"]))
            elif de_plan["start"] <= act_start_minutes:
                new_plan.extend(
                    [
                        _plan_des(de_start, action.start, de_plan["describe"]),
                        _plan_des(
                            action.start, action.end, action.event.get_describe(False)
                        ),
                    ]
                )

        original_plan, new_plan = "\n".join(original_plan), "\n".join(new_plan)

        prompt = self.build_prompt(
            "schedule_revise",
            {
                "agent": self.name,
                "start": start,
                "end": end,
                "original_plan": original_plan,
                "duration": action.duration,
                "event": action.event.get_describe(),
                "new_plan": new_plan,
            }
        )

        def _callback(response):
            import re
            # 全記号対応の包括的パターン
            pattern = r"^\[(\d{1,2}:\d{1,2})\s*[-–—~至]\s*(\d{1,2}:\d{1,2})\]\s*(.*)"
            
            schedules = []
            lines = response.strip().split('\n')
            
            for line in lines:
                line = line.strip()
                if not line:
                    continue
                    
                match = re.match(pattern, line)
                if match:
                    start, end, describe = match.groups()
                    schedules.append((start.strip(), end.strip(), describe.strip()))
            
            decompose = []
            for start, end, describe in schedules:
                m_start = utils.daily_duration(utils.to_date(start, "%H:%M"))
                m_end = utils.daily_duration(utils.to_date(end, "%H:%M"))
                decompose.append(
                    {
                        "idx": len(decompose),
                        "describe": describe,
                        "start": m_start,
                        "duration": m_end - m_start,
                    }
                )
            
            if decompose:
                return decompose
            raise Exception("No valid schedule format found")

        return {"prompt": prompt, "callback": _callback, "failsafe": plan["decompose"]}

    def prompt_determine_sector(self, describes, spatial, address, tile):
        live_address = spatial.find_address("living_area", as_list=True)[:-1]
        curr_address = tile.get_address("sector", as_list=True)

        prompt = self.build_prompt(
            "determine_sector",
            {
                "agent": self.name,
                "live_sector": live_address[-1],
                "live_arenas": ", ".join(i for i in spatial.get_leaves(live_address)),
                "current_sector": curr_address[-1],
                "current_arenas": ", ".join(i for i in spatial.get_leaves(curr_address)),
                "daily_plan": self.config["daily_plan"],
                "areas": ", ".join(i for i in spatial.get_leaves(address)),
                "complete_plan": describes[0],
                "decomposed_plan": describes[1],
            }
        )

        sectors = spatial.get_leaves(address)
        arenas = {}
        for sec in sectors:
            arenas.update(
                {a: sec for a in spatial.get_leaves(address + [sec]) if a not in arenas}
            )
        failsafe = random.choice(sectors)

        def _callback(response):
            patterns = [
                ".*が行くべき場所[:：]\\s*(.*)。?",
                ".*が行くべき場所[:：]\\s*(.*)",
                ".*行くべき[:： ]*(.*)。",
                ".*行くべき[:： ]*(.*)",
                "(.+)。",
                "(.+)",
            ]
            sector = parse_llm_output(response, patterns)
            if sector in sectors:
                return sector
            if sector in arenas:
                return arenas[sector]
            for s in sectors:
                if sector.startswith(s):
                    return s
            return failsafe

        return {"prompt": prompt, "callback": _callback, "failsafe": failsafe}

    def prompt_determine_arena(self, describes, spatial, address):
        prompt = self.build_prompt(
            "determine_arena",
            {
                "agent": self.name,
                "target_sector": address[-1],
                "target_arenas": ", ".join(i for i in spatial.get_leaves(address)),
                "daily_plan": self.config["daily_plan"],
                "complete_plan": describes[0],
                "decomposed_plan": describes[1],
            }
        )

        arenas = spatial.get_leaves(address)
        failsafe = random.choice(arenas)

        def _callback(response):
            patterns = [
                ".*が行くべき場所[:：]\\s*(.*)。?",
                ".*が行くべき場所[:：]\\s*(.*)",
                ".*行くべき[:： ]*(.*)。",
                ".*行くべき[:： ]*(.*)",
                "(.+)。",
                "(.+)",
            ]
            arena = parse_llm_output(response, patterns)
            return arena if arena in arenas else failsafe

        return {"prompt": prompt, "callback": _callback, "failsafe": failsafe}

    def prompt_determine_object(self, describes, spatial, address):
        objects = spatial.get_leaves(address)

        prompt = self.build_prompt(
            "determine_object",
            {
                "activity": describes[1],
                "objects": ", ".join(objects),
            }
        )

        failsafe = random.choice(objects)

        def _callback(response):
            # pattern = ["The most relevant object from the Objects is: <(.+?)>", "<(.+?)>"]
            patterns = [
                ".*オブジェクト[:：]\\s*(.*)。?",
                ".*オブジェクト[:：]\\s*(.*)",
                ".*は[:： ]*(.*)。",
                ".*は[:： ]*(.*)",
                "(.+)。",
                "(.+)",
            ]
            obj = parse_llm_output(response, patterns)
            return obj if obj in objects else failsafe

        return {"prompt": prompt, "callback": _callback, "failsafe": failsafe}

    def prompt_describe_emoji(self, describe):
        prompt = self.build_prompt(
            "describe_emoji",
            {
                "action": describe,
            }
        )

        def _callback(response):
            # 正则表达式：匹配大多数emoji
            emoji_pattern = u"([\U0001F600-\U0001F64F]|"   # 表情符号
            emoji_pattern += u"[\U0001F300-\U0001F5FF]|"   # 符号和图标
            emoji_pattern += u"[\U0001F680-\U0001F6FF]|"   # 运输和地图符号
            emoji_pattern += u"[\U0001F700-\U0001F77F]|"   # 午夜符号
            emoji_pattern += u"[\U0001F780-\U0001F7FF]|"   # 英镑符号
            emoji_pattern += u"[\U0001F800-\U0001F8FF]|"   # 合成扩展
            emoji_pattern += u"[\U0001F900-\U0001F9FF]|"   # 补充符号和图标
            emoji_pattern += u"[\U0001FA00-\U0001FA6F]|"   # 补充符号和图标
            emoji_pattern += u"[\U0001FA70-\U0001FAFF]|"   # 补充符号和图标
            emoji_pattern += u"[\U00002702-\U000027B0]+)"  # 杂项符号

            emoji = re.compile(emoji_pattern, flags=re.UNICODE).findall(response)
            if len(emoji) > 0:
                response = "Emoji: " + "".join(i for i in emoji)
            else:
                response = ""

            return parse_llm_output(response, ["Emoji: (.*)"])[:3]

        return {"prompt": prompt, "callback": _callback, "failsafe": "💭", "retry": 1}

    def prompt_describe_event(self, subject, describe, address, emoji=None):
        prompt = self.build_prompt(
            "describe_event",
            {
                "action": describe,
            }
        )

        e_describe = describe.replace("(", "").replace(")", "").replace("<", "").replace(">", "")
        if e_describe.startswith(subject + "現在"):
            e_describe = e_describe.replace(subject + "現在", "")
        failsafe = Event(
            subject, "現在", e_describe, describe=describe, address=address, emoji=emoji
        )

        def _callback(response):
            response_list = response.replace(")", ")\n").split("\n")
            for response in response_list:
                if len(response.strip()) < 7:
                    continue
                if response.count("(") > 1 or response.count(")") > 1 or response.count("（") > 1 or response.count("）") > 1:
                    continue

                patterns = [
                    "[\(（]<(.+?)>[,， ]+<(.+?)>[,， ]+<(.*)>[\)）]",
                    "[\(（](.+?)[,， ]+(.+?)[,， ]+(.*)[\)）]",
                ]
                outputs = parse_llm_output(response, patterns)
                if len(outputs) == 3:
                    return Event(*outputs, describe=describe, address=address, emoji=emoji)

            return None

        return {"prompt": prompt, "callback": _callback, "failsafe": failsafe}

    def prompt_describe_object(self, obj, describe):
        prompt = self.build_prompt(
            "describe_object",
            {
                "object": obj,
                "agent": self.name,
                "action": describe,
            }
        )

        def _callback(response):
            import re
            # デバッグ用出力
            print(f"[DEBUG] describe_object response: {response}")
            
            # オブジェクト名を正規表現用にエスケープ
            escaped_obj = re.escape(obj)
            
            # まず元のオブジェクト名でマッチを試みる
            patterns_specific = [
                # 標準パターン（山括弧あり、半角コロン）
                f"出力：<{escaped_obj}>: (.*)。?",
                f"出力：<{escaped_obj}>: (.*)",
                f"出力：<{escaped_obj}>:(.*)。?",
                f"出力：<{escaped_obj}>:(.*)",
                f"<{escaped_obj}>: (.*)。?", 
                f"<{escaped_obj}>: (.*)",
                f"<{escaped_obj}>:(.*)。?",
                f"<{escaped_obj}>:(.*)",
                # 全角コロンパターン（山括弧あり）
                f"出力：<{escaped_obj}>： (.*)。?",
                f"出力：<{escaped_obj}>： (.*)",
                f"出力：<{escaped_obj}>：(.*)。?",
                f"出力：<{escaped_obj}>：(.*)",
                f"<{escaped_obj}>： (.*)。?", 
                f"<{escaped_obj}>： (.*)",
                f"<{escaped_obj}>：(.*)。?",
                f"<{escaped_obj}>：(.*)",
                # 山括弧なしパターン（半角コロン）
                f"出力：{escaped_obj}: (.*)。?",
                f"出力：{escaped_obj}: (.*)",
                f"出力：{escaped_obj}:(.*)。?",
                f"出力：{escaped_obj}:(.*)",
                f"{escaped_obj}: (.*)。?", 
                f"{escaped_obj}: (.*)",
                f"{escaped_obj}:(.*)。?",
                f"{escaped_obj}:(.*)",
                # 山括弧なしパターン（全角コロン）
                f"出力：{escaped_obj}： (.*)。?",
                f"出力：{escaped_obj}： (.*)",
                f"出力：{escaped_obj}：(.*)。?",
                f"出力：{escaped_obj}：(.*)",
                f"{escaped_obj}： (.*)。?", 
                f"{escaped_obj}： (.*)",
                f"{escaped_obj}：(.*)。?",
                f"{escaped_obj}：(.*)",
                # 後方互換性のための古いパターン
                f"出力：<{escaped_obj}>(.*)。?",
                f"出力：<{escaped_obj}>(.*)",
            ]
            
            result = parse_llm_output(response, patterns_specific)
            
            # 特定のオブジェクト名でマッチしなかった場合、汎用パターンを試す
            if not result:
                patterns_generic = [
                    # 汎用パターン（任意のオブジェクト名を許可）
                    r"出力：<[^>]+>:\s*(.*)。?",
                    r"出力：<[^>]+>:\s*(.*)",
                    r"出力：<[^>]+>:(.*)。?",
                    r"出力：<[^>]+>:(.*)",
                    r"<[^>]+>:\s*(.*)。?",
                    r"<[^>]+>:\s*(.*)",
                    r"<[^>]+>:(.*)。?",
                    r"<[^>]+>:(.*)",
                    # 全角コロン版
                    r"出力：<[^>]+>：\s*(.*)。?",
                    r"出力：<[^>]+>：\s*(.*)",
                    r"出力：<[^>]+>：(.*)。?",
                    r"出力：<[^>]+>：(.*)",
                    r"<[^>]+>：\s*(.*)。?",
                    r"<[^>]+>：\s*(.*)",
                    r"<[^>]+>：(.*)。?",
                    r"<[^>]+>：(.*)",
                    # 最終フォールバック - コロンの後の内容を取得
                    r"[:：]\s*([^<>\n]+?)(?:。|$)",
                ]
                result = parse_llm_output(response, patterns_generic)
                if result:
                    print(f"[DEBUG] Used generic pattern to extract: {result}")
            
            # 結果を完全な形式で返す（常に元のオブジェクト名を使用）
            if result and result.strip():
                return f"<{obj}>: {result.strip()}"
            
            # パターンマッチに失敗した場合
            print(f"[DEBUG] No pattern matched for object '{obj}' in response: {response[:200]}")
            return f"<{obj}>: 不明"

        return {"prompt": prompt, "callback": _callback, "failsafe": "空いている"}

    def prompt_decide_chat(self, agent, other, focus, chats):
        def _status_des(a):
            event = a.get_event()
            if a.path:
                return f"{a.name} は {event.get_describe(False)} に向かっている"
            return event.get_describe()

        context = "。".join(
            [c.describe for c in focus["events"]]
        )
        context += "\n" + "。".join([c.describe for c in focus["thoughts"]])
        date_str = utils.get_timer().get_date("%Y-%m-%d %H:%M:%S")
        chat_history = ""
        if chats:
            chat_history = f" {agent.name} と {other.name} は前回 {chats[0].create} に {chats[0].describe} について話した"
        a_des, o_des = _status_des(agent), _status_des(other)

        prompt = self.build_prompt(
            "decide_chat",
            {
                "context": context,
                "date": date_str,
                "chat_history": chat_history,
                "agent_status": a_des,
                "another_status": o_des,
                "agent": agent.name,
                "another": other.name,
            }
        )

        def _callback(response):
            if "No" in response or "no" in response or "いいえ" in response or "違う" in response or "違います" in response:
                return False
            return True

        return {"prompt": prompt, "callback": _callback, "failsafe": False}

    def prompt_decide_chat_terminate(self, agent, other, chats):
        conversation = "\n".join(["{}: {}".format(n, u) for n, u in chats])
        conversation = (
            conversation or "[会話はまだ開始されていない]"
        )

        prompt = self.build_prompt(
            "decide_chat_terminate",
            {
                "conversation": conversation,
                "agent": agent.name,
                "another": other.name,
            }
        )

        def _callback(response):
            if "No" in response or "no" in response or "いいえ" in response or "違う" in response or "違います" in response:
                return False
            return True

        return {"prompt": prompt, "callback": _callback, "failsafe": False}

    def prompt_decide_wait(self, agent, other, focus):
        example1 = self.build_prompt(
            "decide_wait_example",
            {
                "context": "簡はリズのルームメイト。2022-10-25 07:05、簡とリズは互いにおはようと挨拶した。",
                "date": "2022-10-25 07:09",
                "agent": "簡",
                "another": "リズ",
                "status": "簡 は浴室に行こうとしている",
                "another_status": "リズ は既に 浴室を使用中",
                "action": "浴室を使用",
                "another_action": "浴室を使用",
                "reason": "推理：簡とリズは両方とも浴室を使いたい。簡とリズが同時に浴室を使うのは変だ。だから、リズが既に浴室を使っているなら、簡にとって最良の選択は浴室の使用を待つことだ。\n",
                "answer": "答案：<選択肢A>",
            }
        )
        example2 = self.build_prompt(
            "decide_wait_example",
            {
                "context": "サムはサラの友人。2022-10-24 23:00、サムとサラは好きな映画について会話した。",
                "date": "2022-10-25 12:40",
                "agent": "サム",
                "another": "サラ",
                "status": "サム は昼食を食べに行こうとしている",
                "another_status": "サラ は既に 洗濯をしている",
                "action": "昼食を食べる",
                "another_action": "洗濯をする",
                "reason": "推理：サムはレストランで昼食を食べるかもしれない。サラは洗濯室で洗濯をするかもしれない。サムとサラは異なるエリアを使用する必要があるため、彼らの行動は競合しない。だから、サムとサラは異なるエリアにいるため、サムは今昼食を続ける。\n",
                "answer": "答案：<選択肢B>",
            }
        )

        def _status_des(a):
            event, loc = a.get_event(), ""
            if event.address:
                loc = " （{} の {} で）".format(event.address[-2], event.address[-1])
            if not a.path:
                return f"{a.name} は既に {event.get_describe(False)}{loc} している"
            return f"{a.name} は {event.get_describe(False)}{loc} しようとしている"

        context = ". ".join(
            [c.describe for c in focus["events"]]
        )
        context += "\n" + ". ".join([c.describe for c in focus["thoughts"]])

        task = self.build_prompt(
            "decide_wait_example",
            {
                "context": context,
                "date": utils.get_timer().get_date("%Y-%m-%d %H:%M"),
                "agent": agent.name,
                "another": other.name,
                "status": _status_des(agent),
                "another_status": _status_des(other),
                "action": agent.get_event().get_describe(False),
                "another_action": other.get_event().get_describe(False),
                "reason": "",
                "answer": "",
            }
        )

        prompt = self.build_prompt(
            "decide_wait",
            {
                "examples_1": example1,
                "examples_2": example2,
                "task": task,
            }
        )

        def _callback(response):
            return "A" in response

        return {"prompt": prompt, "callback": _callback, "failsafe": False}

    def prompt_summarize_relation(self, agent, other_name):
        nodes = agent.associate.retrieve_focus([other_name], 50)

        prompt = self.build_prompt(
            "summarize_relation",
            {
                "context": "\n".join(["{}. {}".format(idx, n.describe) for idx, n in enumerate(nodes)]),
                "agent": agent.name,
                "another": other_name,
            }
        )

        def _callback(response):
            return response

        return {
            "prompt": prompt,
            "callback": _callback,
            "failsafe": agent.name + " が " + other_name + " を見ている",
        }

    def prompt_generate_chat(self, agent, other, relation, chats):
        focus = [relation, other.get_event().get_describe()]
        if len(chats) > 4:
            focus.append("; ".join("{}: {}".format(n, t) for n, t in chats[-4:]))
        nodes = agent.associate.retrieve_focus(focus, 15)
        memory = "\n- " + "\n- ".join([n.describe for n in nodes])
        chat_nodes = agent.associate.retrieve_chats(other.name)
        pass_context = ""
        for n in chat_nodes:
            delta = utils.get_timer().get_delta(n.create)
            if delta > 480:
                continue
            pass_context += f"{delta} 分前、{agent.name} と {other.name} は会話をした。{n.describe}\n"

        address = agent.get_tile().get_address()
        if len(pass_context) > 0:
            prev_context = f'\n背景：\n"""\n{pass_context}"""\n\n'
        else:
            prev_context = ""
        curr_context = (
            f"{agent.name} {agent.get_event().get_describe(False)} 时，看到 {other.name} {other.get_event().get_describe(False)}。"
        )

        conversation = "\n".join(["{}: {}".format(n, u) for n, u in chats])
        conversation = (
            conversation or "[会話はまだ開始されていない]"
        )

        prompt = self.build_prompt(
            "generate_chat",
            {
                "agent": agent.name,
                "base_desc": self._base_desc(),
                "memory": memory,
                "address": f"{address[-2]}，{address[-1]}",
                "current_time": utils.get_timer().get_date("%H:%M"),
                "previous_context": prev_context,
                "current_context": curr_context,
                "another": other.name,
                "conversation": conversation,
            }
        )

        def _callback(response):
            assert "{" in response and "}" in response
            json_content = utils.load_dict(
                "{" + response.split("{")[1].split("}")[0] + "}"
            )
            text = json_content[agent.name].replace("\n\n", "\n").strip(" \n\"'“”‘’")
            return text

        return {
            "prompt": prompt,
            "callback": _callback,
            "failsafe": "うん",
        }

    def prompt_generate_chat_check_repeat(self, agent, chats, content):
        conversation = "\n".join(["{}: {}".format(n, u) for n, u in chats])
        conversation = (
                conversation or "[会話はまだ開始されていない]"
        )

        prompt = self.build_prompt(
            "generate_chat_check_repeat",
            {
                "conversation": conversation,
                "content": f"{agent.name}: {content}",
                "agent": agent.name,
            }
        )

        def _callback(response):
            if "No" in response or "no" in response or "いいえ" in response or "違う" in response or "違います" in response:
                return False
            return True

        return {"prompt": prompt, "callback": _callback, "failsafe": False}

    def prompt_summarize_chats(self, chats):
        conversation = "\n".join(["{}: {}".format(n, u) for n, u in chats])

        prompt = self.build_prompt(
            "summarize_chats",
            {
                "conversation": conversation,
            }
        )

        def _callback(response):
            return response.strip()

        if len(chats) > 1:
            failsafe = "{}と{}の普通の会話".format(chats[0][0], chats[1][0])
        else:
            failsafe = "{}の発言に返事がない".format(chats[0][0])

        return {
            "prompt": prompt,
            "callback": _callback,
            "failsafe": failsafe,
        }

    def prompt_reflect_focus(self, nodes, topk):
        prompt = self.build_prompt(
            "reflect_focus",
            {
                "reference": "\n".join(["{}. {}".format(idx, n.describe) for idx, n in enumerate(nodes)]),
                "number": topk,
            }
        )

        def _callback(response):
            pattern = ["^\d{1}\. (.*)", "^\d{1}\) (.*)", "^\d{1} (.*)"]
            return parse_llm_output(response, pattern, mode="match_all")

        return {
            "prompt": prompt,
            "callback": _callback,
            "failsafe": [
                "{} は誰ですか？".format(self.name),
                "{} はどこに住んでいますか？".format(self.name),
                "{} は今日何をすべきか？".format(self.name),
            ],
        }

    def prompt_reflect_insights(self, nodes, topk):
        prompt = self.build_prompt(
            "reflect_insights",
            {
                "reference": "\n".join(["{}. {}".format(idx, n.describe) for idx, n in enumerate(nodes)]),
                "number": topk,
            }
        )

        def _callback(response):
            import re
            insights = []
            lines = response.strip().split('\n')
            
            for line in lines:
                line = line.strip()
                if not line:
                    continue
                
                # セミコロン区切りのパターン
                match = re.match(r"^([^;]+);([0-9,\s]+)$", line)
                if match:
                    insight = match.group(1).strip()
                    indices_str = match.group(2).strip()
                    indices = [int(i.strip()) for i in indices_str.split(',') if i.strip().isdigit()]
                    node_ids = [nodes[i].node_id for i in indices if i < len(nodes)]
                    insights.append([insight, node_ids])
                else:
                    # フォールバック：見解のみ（番号なし）
                    match = re.match(r"^([^;]+)$", line)
                    if match:
                        insight = match.group(1).strip()
                        node_ids = []
                        insights.append([insight, node_ids])
            
            if insights:
                return insights
            raise Exception("Can not find insights")

        return {
            "prompt": prompt,
            "callback": _callback,
            "failsafe": [
                [
                    "{} は次のステップを検討しています".format(self.name),
                    [nodes[0].node_id] if nodes else [],
                ]
            ],
        }

    def prompt_reflect_chat_planing(self, chats):
        all_chats = "\n".join(["{}: {}".format(n, c) for n, c in chats])

        prompt = self.build_prompt(
            "reflect_chat_planing",
            {
                "conversation": all_chats,
                "agent": self.name,
            }
        )

        def _callback(response):
            return response

        return {
            "prompt": prompt,
            "callback": _callback,
            "failsafe": f"{self.name} 会話をした",
        }

    def prompt_reflect_chat_memory(self, chats):
        all_chats = "\n".join(["{}: {}".format(n, c) for n, c in chats])

        prompt = self.build_prompt(
            "reflect_chat_memory",
            {
                "conversation": all_chats,
                "agent": self.name,
            }
        )

        def _callback(response):
            return response

        return {
            "prompt": prompt,
            "callback": _callback,
            # "failsafe": f"{self.name} had a sonversation",
            "failsafe": f"{self.name} 会話をした",
        }

    def prompt_retrieve_plan(self, nodes):
        statements = [
            n.create.strftime("%Y-%m-%d %H:%M") + ": " + n.describe for n in nodes
        ]

        prompt = self.build_prompt(
            "retrieve_plan",
            {
                "description": "\n".join(statements),
                "agent": self.name,
                "date": utils.get_timer().get_date("%Y-%m-%d"),
            }
        )

        def _callback(response):
            pattern = [
                "^\d{1,2}\. (.*)。",
                "^\d{1,2}\. (.*)",
                "^\d{1,2}\) (.*)。",
                "^\d{1,2}\) (.*)",
            ]
            return parse_llm_output(response, pattern, mode="match_all")

        return {
            "prompt": prompt,
            "callback": _callback,
            "failsafe": [r.describe for r in random.choices(nodes, k=5)],
        }

    def prompt_retrieve_thought(self, nodes):
        statements = [
            n.create.strftime("%Y-%m-%d %H:%M") + "：" + n.describe for n in nodes
        ]

        prompt = self.build_prompt(
            "retrieve_thought",
            {
                "description": "\n".join(statements),
                "agent": self.name,
            }
        )

        def _callback(response):
            return response

        return {
            "prompt": prompt,
            "callback": _callback,
            "failsafe": "{}は昨日のスケジュールに従うべきだ".format(self.name),
        }

    def prompt_retrieve_currently(self, plan_note, thought_note):
        time_stamp = (
            utils.get_timer().get_date() - datetime.timedelta(days=1)
        ).strftime("%Y-%m-%d")

        prompt = self.build_prompt(
            "retrieve_currently",
            {
                "agent": self.name,
                "time": time_stamp,
                "currently": self.currently,
                "plan": ". ".join(plan_note),
                "thought": thought_note,
                "current_time": utils.get_timer().get_date("%Y-%m-%d"),
            }
        )

        def _callback(response):
            pattern = [
                "^状態[:：] (.*)。",
                "^状態[:：] (.*)",
                "^状態(.*)。",
                "^状態(.*)",
            ]
            return parse_llm_output(response, pattern)

        return {
            "prompt": prompt,
            "callback": _callback,
            "failsafe": self.currently,
        }
