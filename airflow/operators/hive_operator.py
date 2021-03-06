import logging
import re

from airflow.hooks import HiveCliHook
from airflow.models import BaseOperator
from airflow.utils import apply_defaults


class HiveOperator(BaseOperator):
    """
    Executes hql code in a specific Hive database.

    :param hql: the hql to be executed
    :type hql: string
    :param hive_cli_conn_id: reference to the Hive database
    :type hive_cli_conn_id: string
    :param hiveconf_jinja_translate: when True, hiveconf-type templating
        ${var} gets translated into jina-type templating {{ var }}
    :type hiveconf_jinja_translate: boolean
    :param script_begin_tag: If defined, the operator will get rid of the
        part of the script before the first occurence of `script_begin_tag`
    :type script_begin_tag: str
    """

    __mapper_args__ = {
        'polymorphic_identity': 'HiveOperator'
    }
    template_fields = ('hql',)
    template_ext = ('.hql', '.sql',)
    ui_color = '#f0e4ec'

    @apply_defaults
    def __init__(
            self, hql,
            hive_cli_conn_id='hive_cli_default',
            hiveconf_jinja_translate=False,
            script_begin_tag=None,
            *args, **kwargs):

        super(HiveOperator, self).__init__(*args, **kwargs)
        self.hiveconf_jinja_translate = hiveconf_jinja_translate
        self.hook = HiveCliHook(hive_cli_conn_id=hive_cli_conn_id)
        self.hql = hql
        self.script_begin_tag = script_begin_tag

    def prepare_template(self):
        if self.hiveconf_jinja_translate:
            self.hql = re.sub(
                "(\$\{([ a-zA-Z0-9_]*)\})", "{{ \g<2> }}", self.hql)
        if self.script_begin_tag and self.script_begin_tag in self.hql:
            self.hql = "\n".join(self.hql.split(self.script_begin_tag)[1:])

    def execute(self, context):
        logging.info('Executing: ' + self.hql)
        self.hook.run_cli(hql=self.hql)

    def on_kill(self):
        self.hook.kill()
