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
        self._network_accuracy = -1
        self._network = 0
        self._count = 0

        self._scale_up_trigger= 0
        self._scale_down_trigger= 0

        #self.set_all()

    def clear(self):
        self._cpu_total = 0
        self._cpu_utilization = 0
        self._network_in = 0
        self._network_out = 0
        self._packet_in = 0
        self._packet_out = 0
        self._cpu_accuracy = -1
        self._network_accuracy = -1
        self._network = 0
        self._count = 0

    def set_all(self, instances):
        self._instances = instances
        self.clear()
        network = 0
        for instance in self._instances:
            if instance.getLifecycleState() == "Running" and instance.getHealthStatus() == "InService":
                self._count += 1
                self._cpu_total += float(instance.getCpuUtilization())
                self._network_in += float(instance.getNetworkIn())
                self._network_out += float(instance.getNetworkOut())
                self._packet_in += float(instance.getNetworkPacketsIn())
                self._packet_out += float(instance.getNetworkPacketsOut())
                network += float(instance.getNetwork())
        
        try:
            self._cpu_utilization =  (self._cpu_total * 100) / (self._count * 100)
            self._network = network / self._count 
            #self._cpu_utilization = float("{:.2f}".format(self._cpu_utilization))
            #self._network = float("{:.2f}".format(self._network))
        except:
            pass
