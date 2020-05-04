import pdfkit


def render(t):
    test = 'localhost/results/%d' % t
    output = '/home/pi/rendered/%d' % t
    pdfkit.from_url(test, output)
    return True


def send():
    return True
