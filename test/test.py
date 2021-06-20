from click.testing import CliRunner
from sf.module.gtpu import gtpu_stat, gtpu_cfg

runner = CliRunner()


def test_gtpu_cfg():
    cfg = {'device_number': '10',
           'bear_timeout_mul': '20',
           'bear_timeout_sec': '30',
           'split_number': '40'
           }
    for key in cfg:
        result = runner.invoke(gtpu_cfg, ['set', key, cfg[key]])
        assert "No Content" in result.output
        assert result.exit_code == 0

    switch = {
        "gtpu_decode": '0',
        'gtpu_inner_decode':'0'
    }

    for key in switch:
        result = runner.invoke(gtpu_cfg, ['enable', key])
        assert "No Content" in result.output
        assert result.exit_code == 0

        result = runner.invoke(gtpu_cfg, ['disable', key])
        assert "No Content" in result.output
        assert result.exit_code == 0

    result = runner.invoke(gtpu_cfg, ['show'])
    assert result.exit_code == 0
    for key in cfg:
        assert cfg[key] in result.output


def test_gtpu_stat():
    result = runner.invoke(gtpu_stat, ['clean'])
    assert result.exit_code == 0
    assert "No Content" in result.output

    stat = ('gtpu_bear_dl_unkown_action', 'gtpu_bear_timer_delete_fail', 'gtpu_bear_ul_unkown_action',
            'gtpu_n3_bear_alloc_failed', 'gtpu_n3_bear_dl_alloc', 'gtpu_n3_bear_dl_free', 'gtpu_n3_bear_recv_err',
            'gtpu_n3_bear_ul_alloc', 'gtpu_n3_bear_ul_free', 'gtpu_n3_dl_bear_recv_count', 'gtpu_n3_dl_match',
            'gtpu_n3_dl_match_err', 'gtpu_n3_dl_miss', 'gtpu_n3_ul_bear_recv_count', 'gtpu_n3_ul_match',
            'gtpu_n3_ul_match_err', 'gtpu_n3_ul_miss', 'gtpu_s1u_bear_alloc_failed', 'gtpu_s1u_bear_dl_alloc',
            'gtpu_s1u_bear_dl_free', 'gtpu_s1u_bear_recv_err', 'gtpu_s1u_bear_ul_alloc', 'gtpu_s1u_bear_ul_free',
            'gtpu_s1u_bear_unkown_diretion', 'gtpu_s1u_dl_bear_recv_count', 'gtpu_s1u_dl_match', 'gtpu_s1u_dl_match_err',
            'gtpu_s1u_dl_miss', 'gtpu_s1u_ul_bear_recv_count', 'gtpu_s1u_ul_match', 'gtpu_s1u_ul_match_err',
            'gtpu_s1u_ul_miss', 'gtpu_total_find_try', 'gtpu_unknow_count', 'n3_baseid_refill_count',
            'n3_dnn_refill_count', 'n3_imei_refill_count', 'n3_imsi_refill_count', 'n3_msisdn_refill_count',
            'n3_tac_refill_count', 's1u_baseid_refill_count', 's1u_dnn_refill_count', 's1u_imei_refill_count',
            's1u_imsi_refill_count', 's1u_msisdn_refill_count', 's1u_tac_refill_count')
    result = runner.invoke(gtpu_stat, ['show'])
    assert result.exit_code == 0
    for i in stat:
        assert i in result.output

