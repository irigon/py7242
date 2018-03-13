import unittest

# A TCP convergence layer shall have one tcp connection.
# When the convergence layer is destroyed, the tcp connection is also destroied
# The send method sends data through the socket connection
# The register method is tested in the "test_convergence_layer" test
# The restart method restarts the socket connection (will that change the descriptor)

class TestTCPCLConnection(unittest.TestCase):

    def setUp(self):
        pass

    def test_creation(self):
        pass


