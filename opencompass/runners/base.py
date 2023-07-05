import getpass
from abc import abstractmethod
from typing import Any, Dict, List, Tuple

from mmengine.config import ConfigDict, Config

from opencompass.utils import LarkReporter, get_logger


class BaseRunner:
    """Base class for all runners. A runner is responsible for launching
    multiple tasks.

    Args:
        task (ConfigDict): Task type config.
        debug (bool): Whether to run in debug mode.
        lark_bot_url (str): Lark bot url.
    """

    def __init__(self,
                 task: ConfigDict,
                 debug: bool = False,
                 lark_bot_url: str = None):
        self.task_cfg = Config(task)
        self.debug = debug
        if lark_bot_url:
            self.lark_reporter = LarkReporter(lark_bot_url)
        else:
            self.lark_reporter = None

    def __call__(self, tasks: List[Dict[str, Any]]):
        """Launch multiple tasks and summarize the results.

        Args:
            tasks (list[dict]): A list of task configs, usually generated by
                Partitioner.
        """
        status = self.launch(tasks)
        self.summarize(status)

    @abstractmethod
    def launch(self, tasks: List[Dict[str, Any]]) -> List[Tuple[str, int]]:
        """Launch multiple tasks.

        Args:
            tasks (list[dict]): A list of task configs, usually generated by
                Partitioner.

        Returns:
            list[tuple[str, int]]: A list of (task name, exit code).
        """

    def summarize(self, status: List[Tuple[str, int]]) -> None:
        """Summarize the results of the tasks.

        Args:
            status (list[tuple[str, int]]): A list of (task name, exit code).
        """

        failed_logs = []
        for _task, code in status:
            if code != 0:
                get_logger().error(f'{_task} failed with code {code}')
                failed_logs.append(_task)
        if self.lark_reporter:
            num_succeeded = len(status) - len(failed_logs)
            if len(failed_logs) > 0:
                content = f'{getpass.getuser()} 的 '
                content += f'{self.task_cfg.type} 任务已完成，'
                content += f'成功任务 {num_succeeded} 个，'
                content += f'失败 {len(failed_logs)} 个。以下为失败的任务列表：'
                content += '\n' + '\n'.join(failed_logs)
                self.lark_reporter.post(title=f'悲报：您有{len(failed_logs)}个'
                                        '任务炸了',
                                        content=content)
            else:
                content = f'{getpass.getuser()} 的 '
                content += f'{self.task_cfg.type} 任务已完成，'
                content += f'成功任务 {num_succeeded} 个。'
                self.lark_reporter.post(title='喜报：全部任务完成', content=content)
