from matplotlib import pyplot as plt
import plotly.graph_objs as go

from MASONmodel.src.features.stats import meanSD_curves

def validation_plot(f_model, data_model, data_exp):
    ExpData_mn, ExpData_SD = meanSD_curves(data_exp)

    fig = go.Figure([
        go.Scatter(
            x=f_model,
            y=data_model,
            line=dict(color='rgb(0,100,80)'),
            mode='lines'
        ),
        go.Scatter(
            x=(data_exp[:, 0, 0] / 10**6),
            y=ExpData_mn,
            line=dict(color='rgb(0,100,80)'),
            mode='lines'
        ),
    #
    #     go.Scatter(
    #         x=x,
    #         y=y,
    #         line=dict(color='rgb(0,100,80)'),
    #         mode='lines'
    #     ),
    #     go.Scatter(
    #         x=x+x[::-1], # x, then x reversed
    #         y=y_upper+y_lower[::-1], # upper, then lower reversed
    #         fill='toself',
    #         fillcolor='rgba(0,100,80,0.2)',
    #         line=dict(color='rgba(255,255,255,0)'),
    #         hoverinfo="skip",
    #         showlegend=False
    #     )
    ])
    fig.update_yaxes(type="log")
    fig.show()


# def validation_plot(f_model, data_model, f_exp, data_exp):
#     fig1 = plt.figure(figsize=(6,5), dpi = 300)
#     ax_1 = fig1.add_subplot(111)
#     ax_1.plot(f, data_model,
#               markersize = 1,
#               color='blue',
#               label = 'x')
#
#     ax_1.plot((ExpData.experiments[1][:, 0] / 10**6), ExpData.experiments[1][:, 6],
#               markersize = 1,
#               color='red',
#               label = 'x')
#
#     plt.yscale('log')
#     ax_1.set_xlabel('Frequency [MHz]')
#     ax_1.set_ylabel('Impedance [Ohm]')
#     plt.grid()
#     #plt.savefig(os.path.join(ARG_EXP_FILE_PATH, 'impedance_curves_improved.png'))
#     plt.show()
#
#     # ax_2 = fig1.add_subplot(212)
#     # ax_2.plot((frequency_spectrum(ARG_FREQUENCY_BAND) / 10**6), np.abs(Z.Z_el),
#     #           markersize = 1,
#     #           color='red',
#     #           label = 'x')
#     # plt.yscale('linear')
#     # ax_2.set_xlabel('Frequency [MHz]')
#     # ax_2.set_ylabel('Impedance [Ohm]')
#     # plt.grid()
#     # plt.show()