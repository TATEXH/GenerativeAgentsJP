import os
import copy
import json
import argparse
import datetime

from dotenv import load_dotenv, find_dotenv

from modules.game import create_game, get_game
from modules import utils

personas = [
    "あいか", "けんじ", "まりあ", "たくみ",  # 学生
    "みどり", "ひろし", "えいじ",  # 家庭：教授、薬店主人、学生
    "さくら", "ともき",  # 家庭：家庭主婦、市場主人
    "かれん", "たまき",  # ルームメイト：供給店主人、児童書作家
    "あつし", "いずみ",  # 酒場の店主、カフェの店主
    "やまだ", "じゅんこ",  # 家庭：退役軍人、水彩画家
    "ふくだ", "はるか", "りょうた", "れいな",  # 共同生活：コメディアン、作家、画家、写真家
    "あきこ", "かずや", "じょうじ", "りゅうじ", "ゆりこ", "あきら",  # アニメーター、詩人、数学者、ソフトウェアエンジニア、税務弁護士、哲学者
]


class SimulateServer:
    def __init__(self, name, static_root, checkpoints_folder, config, start_step=0, verbose="info", log_file=""):
        self.name = name
        self.static_root = static_root
        self.checkpoints_folder = checkpoints_folder

        # 历史存档数据（用于断点恢复）
        self.config = config

        os.makedirs(checkpoints_folder, exist_ok=True)

        # 载入历史对话数据（用于断点恢复）
        self.conversation_log = f"{checkpoints_folder}/conversation.json"
        if os.path.exists(self.conversation_log):
            with open(self.conversation_log, "r", encoding="utf-8") as f:
                conversation = json.load(f)
        else:
            conversation = {}

        if len(log_file) > 0:
            self.logger = utils.create_file_logger(f"{checkpoints_folder}/{log_file}", verbose)
        else:
            self.logger = utils.create_io_logger(verbose)

        # 创建游戏
        game = create_game(name, static_root, config, conversation, logger=self.logger)
        game.reset_game()

        self.game = get_game()
        self.tile_size = self.game.maze.tile_size
        self.agent_status = {}
        if "agent_base" in config:
            agent_base = config["agent_base"]
        else:
            agent_base = {}
        for agent_name, agent in config["agents"].items():
            agent_config = copy.deepcopy(agent_base)
            agent_config.update(self.load_static(agent["config_path"]))
            self.agent_status[agent_name] = {
                "coord": agent_config["coord"],
                "path": [],
            }
        self.think_interval = max(
            a.think_config["interval"] for a in self.game.agents.values()
        )
        self.start_step = start_step

    def simulate(self, step, stride=0):
        timer = utils.get_timer()
        for i in range(self.start_step, self.start_step + step):
            title = "Simulate Step[{}/{}, time: {}]".format(i+1, self.start_step + step, timer.get_date())
            self.logger.info("\n" + utils.split_line(title, "="))
            for name, status in self.agent_status.items():
                plan = self.game.agent_think(name, status)["plan"]
                agent = self.game.get_agent(name)
                if name not in self.config["agents"]:
                    self.config["agents"][name] = {}
                self.config["agents"][name].update(agent.to_dict())
                if plan.get("path"):
                    status["coord"], status["path"] = plan["path"][-1], []
                self.config["agents"][name].update(
                    # {"coord": status["coord"], "path": plan["path"]}
                    {"coord": status["coord"]}
                )

            sim_time = timer.get_date("%Y%m%d-%H:%M")
            self.config.update(
                {
                    "time": sim_time,
                    "step": i + 1,
                }
            )
            # 保存Agent活动数据
            with open(f"{self.checkpoints_folder}/simulate-{sim_time.replace(':', '')}.json", "w", encoding="utf-8") as f:
                f.write(json.dumps(self.config, indent=2, ensure_ascii=False))
            # 保存对话数据
            with open(f"{self.checkpoints_folder}/conversation.json", "w", encoding="utf-8") as f:
                f.write(json.dumps(self.game.conversation, indent=2, ensure_ascii=False))

            if stride > 0:
                timer.forward(stride)

    def load_static(self, path):
        return utils.load_dict(os.path.join(self.static_root, path))


# 从存档数据中载入配置，用于断点恢复
def get_config_from_log(checkpoints_folder):
    files = sorted(os.listdir(checkpoints_folder))

    json_files = list()
    for file_name in files:
        if file_name.endswith(".json") and file_name != "conversation.json":
            json_files.append(os.path.join(checkpoints_folder, file_name))

    if len(json_files) < 1:
        return None

    with open(json_files[-1], "r", encoding="utf-8") as f:
        config = json.load(f)

    assets_root = os.path.join("assets", "village")

    start_time = datetime.datetime.strptime(config["time"], "%Y%m%d-%H:%M")
    start_time += datetime.timedelta(minutes=config["stride"])
    config["time"] = {"start": start_time.strftime("%Y%m%d-%H:%M")}
    agents = config["agents"]
    for a in agents:
        config["agents"][a]["config_path"] = os.path.join(assets_root, "agents", a.replace(" ", "_"), "agent.json")

    return config


# 为新游戏创建配置
def get_config(start_time="20240213-09:30", stride=15, agents=None):
    with open("data/config.json", "r", encoding="utf-8") as f:
        json_data = json.load(f)
        agent_config = json_data["agent"]

    assets_root = os.path.join("assets", "village")
    config = {
        "stride": stride,
        "time": {"start": start_time},
        "maze": {"path": os.path.join(assets_root, "maze.json")},
        "agent_base": agent_config,
        "agents": {},
    }
    for a in agents:
        config["agents"][a] = {
            "config_path": os.path.join(
                assets_root, "agents", a.replace(" ", "_"), "agent.json"
            ),
        }
    return config


def select_agents(agents_arg, all_personas):
    """コマンドライン引数に基づいてエージェントを選択"""
    if agents_arg is None:
        return all_personas
    
    # 数値の場合
    if agents_arg.isdigit():
        num = int(agents_arg)
        if num > len(all_personas):
            print(f"⚠️  指定された人数 {num} が利用可能な人数 {len(all_personas)} を超えています。全員を使用します。")
            return all_personas
        selected = all_personas[:num]
        print(f"✅ 最初の {num} 人のエージェントを使用: {', '.join(selected)}")
        return selected
    
    # 名前のカンマ区切りの場合
    selected = [name.strip() for name in agents_arg.split(',')]
    valid = [name for name in selected if name in all_personas]
    invalid = [name for name in selected if name not in all_personas]
    
    if invalid:
        print(f"⚠️  無効なエージェント名: {', '.join(invalid)}")
    
    if not valid:
        print(f"⚠️  有効なエージェントが見つかりません。全員を使用します。")
        return all_personas
    
    print(f"✅ 選択されたエージェント: {', '.join(valid)}")
    return valid


def update_config_with_poignancy(config, poignancy):
    """内省閾値をconfigに適用"""
    if poignancy is not None:
        if poignancy < 10:
            print(f"⚠️  内省閾値 {poignancy} が小さすぎます。頻繁な内省により処理が遅くなる可能性があります。")
        
        if "agent_base" in config:
            config["agent_base"]["think"]["poignancy_max"] = poignancy
        else:
            # agent_baseがない場合は作成
            if "agent_base" not in config:
                config["agent_base"] = {"think": {}}
            elif "think" not in config["agent_base"]:
                config["agent_base"]["think"] = {}
            config["agent_base"]["think"]["poignancy_max"] = poignancy
        
        print(f"✅ 内省閾値を {poignancy} に設定しました")
    return config


load_dotenv(find_dotenv())

parser = argparse.ArgumentParser(description="console for village")
parser.add_argument("--name", type=str, default="", help="The simulation name")
parser.add_argument("--start", type=str, default="20240213-09:30", help="The starting time of the simulated ville")
parser.add_argument("--resume", action="store_true", help="Resume running the simulation")
parser.add_argument("--step", type=int, default=10, help="The simulate step")
parser.add_argument("--stride", type=int, default=10, help="The step stride in minute")
parser.add_argument("--verbose", type=str, default="debug", help="The verbose level")
parser.add_argument("--log", type=str, default="", help="Name of the log file")
parser.add_argument("--agents", type=str, default=None, help="Number of agents or comma-separated agent names")
parser.add_argument("--poignancy", type=int, default=None, help="Poignancy threshold for reflection (default: 150)")
args = parser.parse_args()


if __name__ == "__main__":
    checkpoints_path = "results/checkpoints"

    name = args.name
    if len(name) < 1:
        name = input("Please enter a simulation name (e.g. sim-test): ")

    resume = args.resume
    if resume:
        while not os.path.exists(f"{checkpoints_path}/{name}"):
            name = input(f"'{name}' doesn't exists, please re-enter the simulation name: ")
    else:
        while os.path.exists(f"{checkpoints_path}/{name}"):
            name = input(f"The name '{name}' already exists, please enter a new name: ")

    checkpoints_folder = f"{checkpoints_path}/{name}"

    start_time = args.start
    if resume:
        sim_config = get_config_from_log(checkpoints_folder)
        if sim_config is None:
            print("No checkpoint file found to resume running.")
            exit(0)
        start_step = sim_config["step"]
        # resumeの場合も内省閾値を更新
        sim_config = update_config_with_poignancy(sim_config, args.poignancy)
    else:
        # エージェントを選択
        selected_personas = select_agents(args.agents, personas)
        sim_config = get_config(start_time, args.stride, selected_personas)
        # 内省閾値を設定
        sim_config = update_config_with_poignancy(sim_config, args.poignancy)
        start_step = 0

    static_root = "frontend/static"

    server = SimulateServer(name, static_root, checkpoints_folder, sim_config, start_step, args.verbose, args.log)
    server.simulate(args.step, args.stride)
