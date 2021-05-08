class Microservice():
    def __init__(self, instances):
        self._instances = instances
        self._cpu_total = 0
        self._cpu_utilization = 0
        self._network_in = 0
        self._network_out = 0
        self._packet_in = 0
        self._packet_out = 0
        self._cpu_accuracy = -1
        self._network_in_accuracy = -1
        self._network_out_accuracy = -1

        self.set_all()

    def set_all(self):
        count = 0
        for instance in self._instances:
            if instance.getLifecycleState() == "Running" and instance.getHealthStatus() == "InService":
                count += 1
                self._cpu_total += float(instance.getCpuUtilization())
                self._network_in += float(instance.getNetworkIn())
                self._network_out += float(instance.getNetworkOut())
                self._packet_in += float(instance.getNetworkPacketsIn())
                self._packet_out += float(instance.getNetworkPacketsOut())

        self._cpu_utilization =  (self._cpu_total * 100) / (count * 100)
