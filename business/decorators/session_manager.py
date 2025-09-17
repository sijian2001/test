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
    """
    
    def __init__(self, func: Callable) -> None:
        self.func = func
        functools.update_wrapper(self, func)
    
    def __call__(self, instance: Any, *args, **kwargs) -> Any:
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
            # セッション開始
            session = instance.db_session.get_session()
            session.begin()
            logger.info("Session started and transaction began")
            
            # デコレートされたメソッドを実行（sessionを第一引数として渡す）
            result = self.func(instance, session, *args, **kwargs)
            
            # 正常終了時はコミット
            session.commit()
            logger.info("Transaction committed successfully")
            return result
            
        except Exception as e:
            # エラー発生時はロールバック
            if session:
                session.rollback()
                logger.error("Transaction rolled back due to error")
            logger.error(f"Error in {self.func.__name__}: {str(e)}")
            raise
        finally:
            # セッションをクローズ
            if session:
                session.close()
                logger.info("Session closed")
    
    def __get__(self, instance, owner):
        """
        デスクリプタプロトコルをサポートして、インスタンスメソッドとして正しく動作させる
        """
        if instance is None:
            return self
        return functools.partial(self.__call__, instance)