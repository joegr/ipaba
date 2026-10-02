import matplotlib

matplotlib.use('Agg')

import matplotlib.pyplot as plt  # noqa: E402

import phonemescape as pm  # noqa: E402


def test_charts_render():
    ipa = pm.Phonemescape()
    for fig in (ipa.plot_vowel_chart(highlight=['i', 'aː']),
                ipa.plot_consonant_chart(highlight=['tʰ']),
                ipa.plot_combined_chart(['i'], ['p']),
                ipa.plot_similarity_network(['i', 'u', 'j', 'w', 'p'], threshold=0.6),
                ipa.plot_similarity_network(['p', 'b', 't'], threshold=0.5)):
        assert fig.axes
    plt.close('all')


def test_charts_inverted():
    ipa = pm.Phonemescape()
    ax = ipa.plot_vowel_chart().axes[0]
    assert ax.get_ylim()[0] > ax.get_ylim()[1]       # close vowels on top
    ax = ipa.plot_consonant_chart().axes[0]
    assert ax.get_ylim()[0] > ax.get_ylim()[1]       # plosives on top
    plt.close('all')
