
import logging

from typing import override
from monero import *


logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(name)s] %(levelname)s: %(message)s")

logger: logging.Logger = logging.getLogger("xmr-sample-python")
logger.setLevel(logging.INFO)


class SyncListener(MoneroWalletListener):

    amount: int | None = None
    funds_received: bool = False
    tx_hash: str | None = None

    @override
    def on_sync_progress(self, height: int, start_height: int, end_height: int, percent_done: float, message: str) -> None:
        # feed a progress bar?
        logger.info(f"Sync progress: {percent_done*100:.2f}% - {message}")

    @override
    def on_output_received(self, output: MoneroOutputWallet) -> None:
        self.amount = output.amount
        self.tx_hash = output.tx_hash
        self.funds_received = True
        logger.info(f"Received funds: {output.amount} XMR")


def main():
    logger.info(f"Sample app using monero-python v{MoneroUtils.get_version()}")
    daemon_uri: str = "http://xmr-node.cakewallet.com:18081"

    # connect to a daemon
    logger.info(f"Connecting to daemon")
    daemon: MoneroDaemonRpc = MoneroDaemonRpc(daemon_uri)
    height: int = daemon.get_height()
    logger.info(f"Daemon height: {height}")

    # create wallet from seed phrase using Python bindings to monero-project
    logger.info(f"Creating wallet from seed phrase")
    config: MoneroWalletConfig = MoneroWalletConfig()
    config.password = "supersecretpassword123"
    config.network_type = MoneroNetworkType.MAINNET
    config.seed = "fruit utensils auburn nabbing huts hexagon espionage fainted oxygen tattoo azure dash phase opened rotate owner grunt happens usage velvet rhythm deepest utensils velvet rotate"
    config.restore_height = height - 1000
    config.server = MoneroRpcConnection(daemon_uri)
    wallet_full: MoneroWalletFull = MoneroWalletFull.create_wallet(config)

    # synchronize with progress notifications
    logger.info("Synchronizing wallet")
    sync_listener: SyncListener = SyncListener()
    wallet_full.sync(sync_listener)

    # synchronize in the background
    wallet_full.start_syncing(20000)

    # listen for incoming transfers
    wallet_full.add_listener(SyncListener())

    # close wallet
    logger.info("Closing wallet")
    wallet_full.close()
    logger.info("Done running XMR sample app")


if __name__ == "__main__":
    main()
