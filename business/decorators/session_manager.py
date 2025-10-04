import functools
import logging
from typing import Callable, Any
from sqlalchemy.orm import Session

logger = logging.getLogger(__name__)

class SessionManager:
    """
    セッション管理を行うデコレーター
    メソッドの実行前にセッションを開始し、正常終了時はコミット、エラー時はロールバック、
    最終的にセッションをクローズする

    Usage:
        @SessionManager(database='test1')
        def some_method(self, input_dto: InDto) -> OutDto:
            pass
    """

    def __init__(self, database: str) -> None:
        """
        Initialize SessionManager decorator

        Args:
            database: Database name ('test1' or 'test2')
        """
        self.database = database

    def __call__(self, func: Callable) -> Callable:
        """
        Decorator implementation

        Args:
            func: Function to be decorated

        Returns:
            Wrapped function
        """
        @functools.wraps(func)
        def wrapper(instance: Any, *args, **kwargs) -> Any:
            """
            デコレートされたメソッドを実行し、セッション管理を行う

            Args:
                instance: デコレートされたメソッドを持つインスタンス
                *args: メソッドの引数
                **kwargs: メソッドのキーワード引数

            Returns:
                メソッドの実行結果
            """
            session = None
            try:
                # データベース別にセッションを取得
                if self.database == 'test1':
                    session = instance.db_session.get_session('test1')
                elif self.database == 'test2':
                    session = instance.db_session.get_session('test2')
                else:
                    raise ValueError(f"Invalid database name: {self.database}")

                session.begin()
                logger.info(f"Session started for {self.database} and transaction began")

                # デコレートされたメソッドを実行（sessionを渡さない）
                result = func(instance, *args, **kwargs)

                # 正常終了時はコミット
                session.commit()
                logger.info(f"Transaction committed successfully for {self.database}")
                return result

            except Exception as e:
                # エラー発生時はロールバック
                if session:
                    session.rollback()
                    logger.error(f"Transaction rolled back due to error for {self.database}")
                logger.error(f"Error in {func.__name__}: {str(e)}")
                raise
            finally:
                # セッションをクローズ
                if session:
                    session.close()
                    logger.info(f"Session closed for {self.database}")

        return wrapper