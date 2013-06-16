"""ProgressBar -- for use with CocoaDialog (http://cocoadialog.sourceforge.net/)"""

__author__ = "Paul Bissex <pb@e-scribe.com>"
__version__ = "0.2.1"
__license__ = "MIT"

import os

class ProgressBar:
    """Simple class for displaying progress bars using CocoaDialog"""

    # Change CD_BASE to reflect the location of Cocoadialog on your system
    CD_BASE = ""
    CD_PATH = os.path.join(CD_BASE, "CocoaDialog.app/Contents/MacOS/CocoaDialog")
    
    def __init__(self, title="Progress", message="", percent=0):
        """Create progress bar dialog"""
        template = "%s progressbar --title '%s' --text '%s' --percent %d"
        self.percent = percent
        self.pipe = os.popen(template % (ProgressBar.CD_PATH, title, message, percent), "w")
        self.message = message
            
    def update(self, percent, message=False):
        """Update progress bar (and message if desired)"""
        if message:
            self.message = message  # store message for persistence
        self.pipe.write("%d %s\n" % (percent, self.message))
        self.pipe.flush()
        
    def finish(self):
        """Close progress bar window"""
        self.pipe.close()


if __name__ == "__main__":
    # Sample usage
    import time
    bar = ProgressBar(title="ProgressBar.py Test")
    
    for percent in range(25):
        time.sleep(.15)
        bar.update(percent, "Test Starting...")
        
    for percent in range(25,100):
        time.sleep(.02)
        bar.update(percent, "Test Finishing...")
     
    time.sleep(.5)
    bar.finish()
