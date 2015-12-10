Changelog
=========

Release 0.2
-----------

Date: 2015 Dec 9

This version introduces three new required parameters
so it can be installed on someone elses compute cluster.

The previous version had a number of hard coded
paths in the condor scripts.

So now you'll need to define

  * star_dir
  * rsem_dir
  * georgi_dir

To define the paths where the pipline code expects to find
several pieces of software.

Release 0.1
-----------

Initial release. It works in my hands, and my coworkers who sits
on the other side of the room from me.