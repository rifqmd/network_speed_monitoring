import re
from datetime import datetime
from collections import defaultdict
from statistics import mean
from bokeh.plotting import figure, output_file, show
from bokeh.models import ColumnDataSource, HoverTool, DatetimeTickFormatter, NumeralTickFormatter, DatetimeTicker


def parse_iperf_data(file_content):
    # Dictionary untuk menyimpan data per jam
    hourly_data = defaultdict(list)

    # Split data berdasarkan sesi test
    sessions = file_content.strip().split('========================================')

    for session in sessions:
        if not session.strip():
            continue

        # Ekstrak timestamp
        timestamp_match = re.search(r'Timestamp: (.*)', session)
        if timestamp_match:
            timestamp = datetime.strptime(timestamp_match.group(1), '%Y-%m-%d %H:%M:%S')

        # Cari baris summary (total bitrate)
        summary_line = None
        lines = session.strip().split('\n')
        for line in lines:
            if 'sender' in line and '0.00-' in line:
                summary_line = line
                break

        if summary_line:
            # Ekstrak total bitrate
            bitrate_match = re.search(r'(\d+\.?\d*)\s+([KMG])bits/sec', summary_line)
            if bitrate_match:
                value = float(bitrate_match.group(1))
                unit = bitrate_match.group(2)

                # Konversi ke Mbps
                if unit == 'K':
                    value = value / 1000
                elif unit == 'G':
                    value = value * 1000

                hourly_data[timestamp].append(value)

    # Urutkan data berdasarkan waktu
    sorted_data = sorted(hourly_data.items())
    timestamps = [item[0] for item in sorted_data]
    bitrates = [mean(item[1]) for item in sorted_data]

    return timestamps, bitrates


def create_network_graph(timestamps, bitrates):
    # Buat ColumnDataSource
    source = ColumnDataSource(data={
        'timestamps': timestamps,
        'bitrates': bitrates
    })

    # Buat figure dengan border
    p = figure(
        width=1200,
        height=400,
        x_axis_type='datetime',
        y_range=(0, 125),
        tools='pan,box_zoom,reset,save,hover',
        toolbar_location='above',
        title='Testing Jaringan'
    )

    # Style judul
    p.title.text_font_size = '20pt'
    p.title.text_font = 'helvetica'
    p.title.text_color = '#666666'
    p.title.align = 'left'

    # Set dan style label axis
    p.xaxis.axis_label = 'DATE TIME'
    p.yaxis.axis_label = 'Speed (Mbps)'
    p.xaxis.axis_label_text_font_size = '10pt'
    p.yaxis.axis_label_text_font_size = '10pt'

    # Konfigurasi grid
    p.xgrid.grid_line_color = '#E0E0E0'
    p.ygrid.grid_line_color = '#E0E0E0'
    p.xgrid.grid_line_alpha = 1
    p.ygrid.grid_line_alpha = 1
    p.grid.grid_line_dash = 'solid'

    # Style background
    p.background_fill_color = 'white'
    p.border_fill_color = 'white'
    p.outline_line_color = 'black'
    p.outline_line_width = 1

    # Tambahkan garis
    p.line('timestamps', 'bitrates',
           line_color='#1f77b4',
           line_width=1.5,
           source=source)

    # Format axis
    p.yaxis.formatter = NumeralTickFormatter(format='0.00')
    p.xaxis.formatter = DatetimeTickFormatter(
        hours='%m/%d/%Y %H:%M:%S',
        days='%m/%d/%Y',
        months='%m/%d/%Y',
        years='%m/%d/%Y'
    )

    # p.xaxis.formatter = DatetimeTickFormatter(
    #     hours='%m/%d/%Y\n%H:00:00',
    #     days='%m/%d/%Y',
    #     months='%m/%d/%Y',
    #     years='%m/%d/%Y'
    # )
    #
    # # Force 6-hour intervals on x-axis ticks
    # p.xaxis.ticker = DatetimeTicker(
    #     desired_num_ticks=int((timestamps[-1] - timestamps[0]).total_seconds() // (6 * 3600)))

    # Format tick labels
    p.xaxis.major_label_text_font_size = '8pt'
    p.yaxis.major_label_text_font_size = '8pt'
    p.xaxis.major_label_orientation = 0

    # Kustomisasi hover tool
    hover = p.select_one(HoverTool)
    hover.tooltips = [
        ('Date', '@timestamps{%Y-%m-%d}'),
        ('Time', '@timestamps{%H:%M:%S}'),
        ('Speed', '@bitrates{0.00} Mbps')
    ]
    hover.formatters = {'@timestamps': 'datetime'}

    return p


# Eksekusi utama
def main():
    # Baca file
    with open('../data/soal_chart_bokeh.txt', 'r') as file:
        file_content = file.read()

    # Parse data
    timestamps, bitrates = parse_iperf_data(file_content)

    # Buat dan simpan plot
    output_file('../result/network_speed_monitoring.html')
    p = create_network_graph(timestamps, bitrates)
    show(p)


if __name__ == '__main__':
    main()