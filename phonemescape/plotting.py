"""
2D plotting of IPA segments, following the IPA chart (2020 revision).

Vowels (trapezoid) and consonants (pulmonic grid) are always drawn on
SEPARATE planes.  Both charts are drawn in the official orientation: close
vowels and the plosive row at the top.
"""

from typing import Dict, Iterable, List, Optional, Set, Tuple

import matplotlib.patches as patches
import matplotlib.pyplot as plt
import numpy as np

from .data import (
    CONSONANT_COORD_INFO, HEIGHT_Y, IPA_CONSONANTS, IPA_VOWELS, VOWEL_COORD_INFO,
    VOWEL_MAX_Y, VOWEL_TRAPEZOID, vowel_back_edge, vowel_central_x, vowel_front_edge,
)
from .segments import Segment, get_segment

SHORT_PLACE_LABELS = ['Bilab.', 'Labiod.', 'Dent.', 'Alv.', 'Postalv.', 'Retro.',
                      'Pal.', 'Vel.', 'Uv.', 'Phar.', 'Glot.']
SHORT_MANNER_LABELS = ['Plosive', 'Nasal', 'Trill', 'Tap/Flap', 'Fricative',
                       'Lat. fric.', 'Approx.', 'Lat. approx.']


def _bases(symbols: Optional[Iterable[str]]) -> Set[str]:
    """Base chart symbols of the given segments (so 'aː' highlights 'a')."""
    out: Set[str] = set()
    for s in symbols or []:
        try:
            out.update(get_segment(s).parts)
        except ValueError:
            continue
    return out


class IPAPlotter:
    """Handles 2D plotting of IPA segments on vowel and consonant charts."""

    def __init__(self) -> None:
        self.fig_size = (12, 8)
        self.vowel_colors = {
            'unrounded': '#FF6B6B',
            'rounded': '#4ECDC4',
            'unspecified': '#C9A0DC',
        }
        self.consonant_colors = {
            'voiceless': '#95A5A6',
            'voiced': '#3498DB',
        }

    # ------------------------------------------------------------------
    # axes set-up (public so callers can build their own figures)
    # ------------------------------------------------------------------

    def setup_vowel_axes(self, ax: plt.Axes, show_grid: bool = True) -> None:
        """Draw the trapezoid, its guide lines and labels on ``ax``."""
        xs, ys = zip(*(VOWEL_TRAPEZOID + VOWEL_TRAPEZOID[:1]))
        ax.plot(xs, ys, 'k-', linewidth=1.2, alpha=0.6)
        for y in (HEIGHT_Y['close-mid'], HEIGHT_Y['open-mid']):
            ax.plot([vowel_front_edge(y), vowel_back_edge(y)], [y, y],
                    'k-', linewidth=0.6, alpha=0.3)
        ax.plot([vowel_central_x(0), vowel_central_x(VOWEL_MAX_Y)], [0, VOWEL_MAX_Y],
                'k-', linewidth=0.6, alpha=0.3)
        ax.set_xlim(*VOWEL_COORD_INFO['x_range'])
        ax.set_ylim(VOWEL_COORD_INFO['y_range'][1], VOWEL_COORD_INFO['y_range'][0])
        ax.set_xticks([vowel_front_edge(0), vowel_central_x(0), vowel_back_edge(0)])
        ax.set_xticklabels([label for _, label in VOWEL_COORD_INFO['x_ticks']])
        ax.set_yticks([t for t, _ in VOWEL_COORD_INFO['y_ticks']])
        ax.set_yticklabels([label for _, label in VOWEL_COORD_INFO['y_ticks']])
        ax.set_xlabel('Backness (Front → Back)')
        ax.set_ylabel('Height (Close → Open)')
        ax.grid(show_grid, alpha=0.15)

    def setup_consonant_axes(self, ax: plt.Axes, short_labels: bool = False,
                             show_grid: bool = True) -> None:
        """Draw the pulmonic grid and labels on ``ax``."""
        if show_grid:
            for x in range(12):
                ax.axvline(x - 0.5, color='gray', linewidth=0.5, alpha=0.3)
            for y in range(9):
                ax.axhline(y - 0.5, color='gray', linewidth=0.5, alpha=0.3)
        ax.set_xlim(*CONSONANT_COORD_INFO['x_range'])
        ax.set_ylim(CONSONANT_COORD_INFO['y_range'][1], CONSONANT_COORD_INFO['y_range'][0])
        ax.set_xticks([t for t, _ in CONSONANT_COORD_INFO['x_ticks']])
        ax.set_xticklabels(SHORT_PLACE_LABELS if short_labels else
                           [label for _, label in CONSONANT_COORD_INFO['x_ticks']],
                           rotation=45, ha='right')
        ax.set_yticks([t for t, _ in CONSONANT_COORD_INFO['y_ticks']])
        ax.set_yticklabels(SHORT_MANNER_LABELS if short_labels else
                           [label for _, label in CONSONANT_COORD_INFO['y_ticks']])
        ax.set_xlabel('Place of Articulation (Front → Back)')
        ax.set_ylabel('Manner of Articulation')

    def _draw_points(self, ax: plt.Axes, table: Dict[str, Tuple], colors: Dict[str, str],
                     color_index: int, highlight: Set[str], sizes: Tuple[int, int],
                     fontsize: int) -> None:
        for symbol, row in table.items():
            x, y = row[0], row[1]
            hl = symbol in highlight
            ax.scatter(x, y, s=sizes[1] if hl else sizes[0], c=colors[row[color_index]],
                       alpha=1.0 if hl or not highlight else 0.45,
                       edgecolors='black', linewidth=2.2 if hl else 1.0, zorder=5)
            ax.annotate(symbol, (x, y), fontsize=fontsize, ha='center', va='center',
                        fontweight='bold', zorder=6)

    def _legend(self, ax: plt.Axes, colors: Dict[str, str], loc: str) -> None:
        ax.legend(handles=[patches.Patch(color=c, label=k.capitalize())
                           for k, c in colors.items()], loc=loc)

    # ------------------------------------------------------------------
    # charts
    # ------------------------------------------------------------------

    def plot_vowel_chart(self, highlight_phonemes: Optional[List[str]] = None,
                         show_grid: bool = True,
                         title: str = "IPA Vowel Chart (Trapezoid)") -> plt.Figure:
        """The 28 vowels of the IPA chart on the trapezoid."""
        fig, ax = plt.subplots(figsize=self.fig_size)
        self.setup_vowel_axes(ax, show_grid)
        self._draw_points(ax, IPA_VOWELS, self.vowel_colors, 4,
                          _bases(highlight_phonemes), (250, 420), 14)
        ax.set_title(title, fontsize=14, fontweight='bold')
        self._legend(ax, self.vowel_colors, 'lower left')
        fig.tight_layout()
        return fig

    def plot_consonant_chart(self, highlight_phonemes: Optional[List[str]] = None,
                             show_grid: bool = True,
                             title: str = "IPA Consonant Chart (Pulmonic)") -> plt.Figure:
        """The 59 pulmonic consonants on the chart grid."""
        fig, ax = plt.subplots(figsize=(14, 8))
        self.setup_consonant_axes(ax, show_grid=show_grid)
        self._draw_points(ax, IPA_CONSONANTS, self.consonant_colors, 4,
                          _bases(highlight_phonemes), (220, 360), 11)
        ax.set_title(title, fontsize=14, fontweight='bold')
        self._legend(ax, self.consonant_colors, 'lower right')
        fig.tight_layout()
        return fig

    def plot_combined_chart(self, highlight_vowels: Optional[List[str]] = None,
                            highlight_consonants: Optional[List[str]] = None,
                            show_grid: bool = True,
                            title: str = "IPA Combined Chart") -> plt.Figure:
        """Vowels and pulmonic consonants side by side, on separate planes."""
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(18, 8),
                                       gridspec_kw={'width_ratios': [1, 1.4]})
        self.setup_vowel_axes(ax1, show_grid)
        self._draw_points(ax1, IPA_VOWELS, self.vowel_colors, 4,
                          _bases(highlight_vowels), (200, 350), 12)
        ax1.set_title('Vowels', fontsize=13, fontweight='bold')
        self._legend(ax1, self.vowel_colors, 'lower left')

        self.setup_consonant_axes(ax2, short_labels=True, show_grid=show_grid)
        self._draw_points(ax2, IPA_CONSONANTS, self.consonant_colors, 4,
                          _bases(highlight_consonants), (180, 300), 10)
        ax2.set_title('Pulmonic consonants', fontsize=13, fontweight='bold')
        self._legend(ax2, self.consonant_colors, 'lower right')

        fig.suptitle(title, fontsize=15, fontweight='bold')
        fig.tight_layout()
        return fig

    # ------------------------------------------------------------------
    # networks
    # ------------------------------------------------------------------

    def draw_network(self, ax: plt.Axes, segments: List[Segment], matrix: np.ndarray,
                     threshold: float, indices: List[int]) -> None:
        """Nodes ``indices`` of one plane and the edges among them."""
        for a in range(len(indices)):
            for b in range(a + 1, len(indices)):
                i, j = indices[a], indices[b]
                sim = matrix[i, j]
                if sim >= threshold:
                    (x1, y1), (x2, y2) = segments[i].coordinates, segments[j].coordinates
                    ax.plot([x1, x2], [y1, y2], color='gray', alpha=float(sim),
                            linewidth=float(sim) * 3, zorder=2)
        for i in indices:
            x, y = segments[i].coordinates
            ax.scatter(x, y, s=420, c='lightblue', edgecolors='black', linewidth=2, zorder=5)
            ax.annotate(segments[i].symbol, (x, y), fontsize=12, ha='center', va='center',
                        fontweight='bold', zorder=6)

    def plot_similarity_network(self, phonemes: List[str], similarity_matrix: np.ndarray,
                                threshold: float = 0.5,
                                title: str = "Phoneme Similarity Network") -> plt.Figure:
        """
        Network of segments placed at their chart positions, with an edge
        wherever similarity >= threshold.  Vowels and consonants are drawn on
        their own planes; edges between a vowel and a consonant are drawn
        dashed across the two panels.
        """
        segs = [get_segment(p) for p in phonemes]
        v_idx = [i for i, s in enumerate(segs) if s.kind == 'vowel']
        c_idx = [i for i, s in enumerate(segs) if s.kind == 'consonant']

        if v_idx and c_idx:
            fig, (axv, axc) = plt.subplots(1, 2, figsize=(18, 8),
                                           gridspec_kw={'width_ratios': [1, 1.4]})
        else:
            fig, ax = plt.subplots(figsize=(10, 8) if v_idx else (14, 8))
            axv = axc = ax
        if v_idx:
            self.setup_vowel_axes(axv)
            self.draw_network(axv, segs, similarity_matrix, threshold, v_idx)
        if c_idx:
            self.setup_consonant_axes(axc, short_labels=bool(v_idx))
            self.draw_network(axc, segs, similarity_matrix, threshold, c_idx)

        if v_idx and c_idx:
            for i in v_idx:
                for j in c_idx:
                    sim = similarity_matrix[i, j]
                    if sim >= threshold:
                        fig.add_artist(patches.ConnectionPatch(
                            xyA=segs[i].coordinates, coordsA=axv.transData,
                            xyB=segs[j].coordinates, coordsB=axc.transData,
                            color='darkorange', linestyle='--', alpha=float(sim),
                            linewidth=float(sim) * 2, zorder=1))
            axv.set_title('Vowels', fontweight='bold')
            axc.set_title('Consonants', fontweight='bold')
            fig.suptitle(f"{title}  (dashed: vowel–consonant edges)",
                         fontsize=14, fontweight='bold')
        else:
            axv.set_title(title, fontsize=14, fontweight='bold')
        fig.tight_layout()
        return fig
