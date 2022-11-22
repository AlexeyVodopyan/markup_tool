# stdlib
import enum

# thirdparty
from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, func
from sqlalchemy.ext.hybrid import Comparator, hybrid_property
from sqlalchemy.orm import declared_attr, deferred, relationship

# project
from common.db_config import Base


class CreatedAtMixin:
    @declared_attr
    def created_at(cls):
        return Column(
            DateTime,
            server_default=func.now(),
            nullable=False,
            comment="Дата создания",
        )


class PasswordMixin:
    @declared_attr
    def password_hashed(cls):
        return deferred(Column(String, comment="Зашифрованный пароль", nullable=False))

    @hybrid_property
    def password(self):
        """Relying upon database-side crypt() only, so in-Python usage
        is notimplemented.

        """
        raise NotImplementedError("Comparison only supported via the database")

    class CryptComparator(Comparator):
        """A Comparator which provides an __eq__() method that will run
        crypt() against both sides of the expression, to provide the
        test password/salt pair.

        """

        def __init__(self, password_hashed):
            self.password_hashed = password_hashed

        def __eq__(self, other):
            return self.password_hashed == func.crypt(other, self.password_hashed)

    @password.comparator
    def password(cls):
        """Provide a Comparator object which calls crypt in the
        appropriate fashion.

        """
        return cls.CryptComparator(cls.password_hashed)

    @password.setter
    def password(self, value):
        """assign the value of 'password',
        using a UOW-evaluated SQL function.

        See http://www.sqlalchemy.org/docs/orm/session.html#embedding-sql-insert-update-expressions-into-a-flush
        for a description of SQL expression assignment.

        """
        self.password_hashed = func.crypt(value, func.gen_salt("md5"))


class TaskStatus(enum.IntEnum):
    ASSIGNED = 0
    RESOLVED = 1


class Image(CreatedAtMixin, Base):
    __tablename__ = "image"

    id = Column(Integer, primary_key=True, comment="ID изображения", autoincrement=True)
    file_path = Column(String, comment="Путь к файлу", nullable=False, unique=True)
    task_id = Column(Integer, ForeignKey("task.id", ondelete="CASCADE"))
    task = relationship("Task")


class LabeledImage(CreatedAtMixin, Base):
    __tablename__ = "labeled_image"

    id = Column(Integer, primary_key=True, comment="ID записи", autoincrement=True)
    image_id = Column(
        Integer, ForeignKey("image.id", ondelete="CASCADE"), primary_key=True
    )
    tg_login = Column(
        String, ForeignKey("tg_user.login", ondelete="CASCADE"), primary_key=True
    )

    label_id = Column(Integer, ForeignKey("label_class.id", ondelete="CASCADE"))

    image = relationship("Image")
    tg_user = relationship("TgUser")
    label_class = relationship("LabelClass")


class LabelClass(CreatedAtMixin, Base):
    __tablename__ = "label_class"

    id = Column(Integer, primary_key=True, comment="ID класса", autoincrement=True)
    name = Column(String, unique=True)


class TaskLabelClass(CreatedAtMixin, Base):
    __tablename__ = "task_label_class"

    id = Column(Integer, primary_key=True, comment="ID записи")
    task_id = Column(Integer, ForeignKey("task.id", ondelete="CASCADE"))
    task = relationship("Task")
    label_class_id = Column(Integer, ForeignKey("label_class.id", ondelete="CASCADE"))
    label_class = relationship("LabelClass")


class Task(CreatedAtMixin, Base):
    __tablename__ = "task"

    id = Column(Integer, primary_key=True, comment="ID задачи", autoincrement=True)
    task_tg_users = relationship("TaskTgUser", back_populates="task")
    images = relationship("Image", back_populates="task")


class TaskTgUser(CreatedAtMixin, Base):
    __tablename__ = "task_tg_user"

    id = Column(Integer, primary_key=True, comment="ID записи")
    task_id = Column(Integer, ForeignKey("task.id", ondelete="CASCADE"))
    task = relationship("Task")
    tg_login = Column(String, ForeignKey("tg_user.login", ondelete="CASCADE"))
    tg_user = relationship("TgUser")
    status = Column(Integer, default=TaskStatus.ASSIGNED, nullable=True)


class TgUser(CreatedAtMixin, PasswordMixin, Base):
    __tablename__ = "tg_user"

    login = Column(String, primary_key=True, comment="Логин")
    task_tg_users = relationship("TaskTgUser", back_populates="tg_user")


class WebUser(CreatedAtMixin, PasswordMixin, Base):
    __tablename__ = "web_user"

    id = Column(Integer, primary_key=True, autoincrement=True)
    login = Column(String(80), comment="логин", unique=True)
