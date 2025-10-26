import cupy as cp


def check_gpu():
    try:
        n_devices = cp.cuda.runtime.getDeviceCount()
        print(f"Number of GPUs detected: {n_devices}")
        for i in range(n_devices):
            with cp.cuda.Device(i) as device:
                props = cp.cuda.runtime.getDeviceProperties(i)
                print(
                    f"GPU {i}: {props['name'].decode('utf-8')} with compute capability {props['major']}.{props['minor']}")
    except Exception as e:
        print("Error detecting GPU:", e)


if __name__ == "__main__":
    check_gpu()
