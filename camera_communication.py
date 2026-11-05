import importlib
import socket

CAMERA_MODULE = "card_reader"  # Kamerafilens navn uten .py
PORT = 5000


def main():
    camera_module = None

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server:
        server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server.bind(("0.0.0.0", PORT))
        server.listen(1)

        print(f"Venter på robot på port {PORT} ...")

        while True:
            conn, address = server.accept()
            print("Robot tilkoblet:", address)

            with conn:
                try:
                    with conn.makefile("rb") as reader:
                        for line in reader:
                            if line.strip() != b"READY":
                                conn.sendall(b"ERROR, COMMAND\n")
                                continue

                            try:
                                # Kjør kamerakoden ved hver READY.
                                if camera_module is None:
                                    camera_module = importlib.import_module(
                                        CAMERA_MODULE
                                    )
                                else:
                                    camera_module = importlib.reload(
                                        camera_module
                                    )

                                card_value = camera_module.card_value

                                if card_value is None:
                                    response = "ERROR, NO_CARD\n"
                                else:
                                    response = "REGISTERED\n"

                            except Exception as error:
                                print("Kamerafeil:", error)
                                response = "ERROR, CAMERA\n"

                            conn.sendall(response.encode("ascii"))
                            print("Sendt:", response.strip())

                except OSError as error:
                    print("Robotforbindelsen ble brutt:", error)


if __name__ == "__main__":
    main()