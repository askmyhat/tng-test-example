import unittest
import docker
import datetime
import time


test_data = [
    ('/', []),
    ('/restricted/', ['Requested restricted content'])
]


class VNFAssertions:
    def assertAlertsMatch(self, expected, actual):
        if len(expected) != len(actual):
            raise AssertionError('Lengths are not equal')
        for i in range(len(expected)):
            if expected[i] not in actual[i]:
                raise AssertionError(expected[i])


class SnortTestCase(unittest.TestCase, VNFAssertions):
    def get_instance_ip(self, instance, if_name):
        command = 'ifconfig {}'.format(if_name)
        ifconfig_output = instance.exec_run(command).decode('utf-8')
        ip_address = ifconfig_output.splitlines()[1].split()[1].split(':')[1]
        return ip_address

    def snort_time_to_timestamp(self, snort_time):
        time_format = '%Y/%m/%d-%H:%M:%S.%f'
        current_year = str(datetime.datetime.now().year)
        record_time = current_year + '/' + snort_time
        time_formatted = datetime.datetime.strptime(record_time, time_format)
        return time_formatted.timestamp()

    def get_alert_updates(self, start_time):
        two_hours_in_seconds = 7200

        result = []

        command = 'cat /snort-logs/alert'
        alert_records = self.snort.exec_run(command).decode('utf-8')
        for record in alert_records.splitlines():
            record_time = record.split()[0]
            record_time_formatted = self.snort_time_to_timestamp(record_time)
            if record_time_formatted + two_hours_in_seconds > start_time:
                result.append(record)

        return result

    def make_request(self, test_input):
        start_time = datetime.datetime.now().timestamp()

        test_command = 'curl {}{}'.format(self.server.ip, test_input)
        test_output = self.client.exec_run(test_command, stream=True)
        for _ in test_output:
            pass
        time.sleep(1)

        output = list(self.get_alert_updates(start_time))

        return output

    def setUp(self):
        self.docker_client = docker.from_env()

        self.client = self.docker_client.containers.get('mn.client')
        self.snort = self.docker_client.containers.get('mn.snort_vnf')
        self.server = self.docker_client.containers.get('mn.server')

        self.server.ip = self.get_instance_ip(self.server, 'server-eth0')

    def tearDown(self):
        pass

    def test_blocking_rules(self):
        for test_case in test_data:
            test_input, expected_output = test_case
            actual_output = self.make_request(test_input)
            with self.subTest(test_case=test_case):
                self.assertAlertsMatch(expected_output, actual_output)


if __name__ == '__main__':
    unittest.main()
