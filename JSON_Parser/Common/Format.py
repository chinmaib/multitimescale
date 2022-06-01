
def secondsToTime(seconds: int):
    minutes = int(seconds / 60)
    seconds = seconds % 60

    if minutes <= 9:
        timer = f"0{minutes}"
    else:
        timer = f"{minutes}"

    if seconds <= 9:
        timer = f"{timer}:0{seconds}"
    else:
        timer = f"{timer}:{seconds}"

    return timer

