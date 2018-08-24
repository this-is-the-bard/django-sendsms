import logging

import boto3
from django.conf import settings

from .base import BaseSmsBackend

logger = logging.getLogger(__name__)

AWS_ACCESS_KEY_ID = getattr(settings, 'AWS_ACCESS_KEY_ID')
AWS_SECRET_ACCESS_KEY = getattr(settings, 'AWS_SECRET_ACCESS_KEY')
AWS_REGION_NAME = getattr(settings, 'AWS_REGION_NAME')
# AWS_SMS_MONTHLY_SPEND_LIMIT = os.environ.get('AWS_SMS_MONTHLY_SPEND_LIMIT', "10")  # In USD
AWS_DEFAULT_SMS_TYPE = getattr(settings, 'AWS_DEFAULT_SMS_TYPE', 'Promotional')


# ----- Regions as at 24/08/2018 ------
# us-east-1         : North Virginia
# us-west-2         : Oregon
# eu-west-1         : Ireland
# ap-northeast-1    : Tokyo
# ap-southeast-1    : Singapore
# ap-southeast-2    : Sydney


class SmsBackend(BaseSmsBackend):
    """
    Wrapper for AWS SNS
    """

    def __init__(self):
        super().__init__()
        for check in [AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY, AWS_REGION_NAME]:
            if not check:
                logger.error("No {} found".format(check))
                raise Exception("No {} found".format(check))

    def _send(self, message, sms_type=AWS_DEFAULT_SMS_TYPE):
        # Setup params for connection
        sns = boto3.client(
            service_name='sns',
            aws_access_key_id=AWS_ACCESS_KEY_ID,
            aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
            region_name=AWS_REGION_NAME,
        )
        sns.set_sms_attributes(
            attributes={
                # 'MonthlySpendLimit': AWS_SMS_MONTHLY_SPEND_LIMIT,
                'DefaultSMSType': AWS_DEFAULT_SMS_TYPE,
            }
        )
        responses = []
        for to in message.to:
            params = {
                'PhoneNumber': to,
                'Message': message.body,
            }
            # Send message
            # Successful if MessageId returned
            r = sns.publish(
                params
            )
            responses.append(r)

        return responses

    def send_messages(self, messages, sms_type=AWS_DEFAULT_SMS_TYPE):
        """
        Sends one or more SmsMessage objects and returns the number of sms
        messages sent.
        :param messages: List of messages to be sent
        :param sms_type: <Promotional/Transactional>. Affects pricing.
        """
        if not messages:
            return

        num_sent = 0
        for message in messages:
            if self._send(message, sms_type=AWS_DEFAULT_SMS_TYPE):
                num_sent += 1
        return num_sent
