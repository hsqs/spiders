## About
Generally, I want to collect some images from a website, I write a simple spider and download what I want. All the envrionment is under Python3, and some other components should be installed.


## Every website matches a spider
There are python spiders in every folder, and if want to run it, you should read following message of one specific folder.

### one  
folder '[one]'(http://wufazhuce.com). To download all images under http://wufazhuce.com/one/-, Just found what is the maximum number at the end of the path(it willed be found in the latest website), and change it in the script of variable *MAX_PAGE_NUM*, and of course *START_PAGE_NUM* is the minimum number if should be configed.


### weibo
folder '[weibo]'(http://weibo.com). To download some of the users' picture you liked, which user and how many pages' pictures will be downloaded can be configed in the script, after running, pictures will be stored in the folder by the user ID. At last, cookie should be replaced as String, which could be found in the browser console.
