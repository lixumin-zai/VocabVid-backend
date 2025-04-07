import logging

def setup_logging():
    # 创建一个过滤器来添加 request_id 到每一条日志记录
    class RequestIdFilter(logging.Filter):
        def filter(self, record):
            # 从线程局部变量或上下文中获取 request_id，如果没有则设置为空字符串
            record.request_id = getattr(record, 'request_id', "")
            return True

    # 获取 root logger
    root_logger = logging.getLogger()
    if not root_logger.handlers:
        root_logger.setLevel(logging.INFO)  # 设置 root logger 的级别

        # 创建一个 StreamHandler，将日志输出到控制台
        stream_handler = logging.StreamHandler()

        # 定义日志格式
        log_format = '%(asctime)s - %(levelname)s - %(request_id)s - %(name)s - line: %(lineno)s - %(funcName)s : %(message)s'
        formatter = logging.Formatter(log_format)
        stream_handler.setFormatter(formatter)

        # 添加过滤器到 handler
        stream_handler.addFilter(RequestIdFilter())

        # 将 handler 添加到 root logger
        root_logger.addHandler(stream_handler)

setup_logging()