
from weibo import weibo_miner


if __name__ == '__main__':
    target = {
        # user_id : page_num
        2811699412: 5,
        2663489000: 933
    }

    wm = weibo_miner.miner(target)
