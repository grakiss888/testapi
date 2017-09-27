##############################################################################
# Copyright (c) 2015 Orange
# guyrodrigue.koffi@orange.com / koffirodrigue@gmail.com
# All rights reserved. This program and the accompanying materials
# are made available under the terms of the Apache License, Version 2.0
# which accompanies this distribution, and is available at
# http://www.apache.org/licenses/LICENSE-2.0
##############################################################################

from opnfv_testapi.resources import handlers
from opnfv_testapi.resources import result_handlers
from opnfv_testapi.resources import test_handlers
from opnfv_testapi.resources import application_handlers
from opnfv_testapi.ui.auth import sign
from opnfv_testapi.ui.auth import user

mappings = [
    # GET /versions => GET API version
    (r"/versions", handlers.VersionHandler),

    # few examples:
    # GET /api/v1/pods => Get all pods
    # GET /api/v1/pods/1 => Get details on POD 1
    #(r"/api/v1/pods", pod_handlers.PodCLHandler),
    #(r"/api/v1/pods/([^/]+)", pod_handlers.PodGURHandler),

    # few examples:
    # GET /projects
    # GET /projects/yardstick
    #(r"/api/v1/projects", project_handlers.ProjectCLHandler),
    #(r"/api/v1/projects/([^/]+)", project_handlers.ProjectGURHandler),

    # few examples
    # GET /projects/qtip/cases => Get cases for qtip
    #(r"/api/v1/projects/([^/]+)/cases", testcase_handlers.TestcaseCLHandler),
    #(r"/api/v1/projects/([^/]+)/cases/([^/]+)",
    # testcase_handlers.TestcaseGURHandler),

    # new path to avoid a long depth
    # GET /results?project=functest&case=keystone.catalog&pod=1
    #   => get results with optional filters
    # POST /results =>
    # Push results with mandatory request payload parameters
    # (project, case, and pod)
    #(r"/api/v1/results", result_handlers.ResultsCLHandler),
    (r"/api/v1/results/upload", result_handlers.ResultsUploadHandler),
    (r"/api/v1/results/([^/]+)", result_handlers.ResultsGURHandler),

    (r"/api/v1/tests", test_handlers.TestsCLHandler),
    (r"/api/v1/tests/([^/]+)", test_handlers.TestsGURHandler),

    (r"/api/v1/cvp/applications", application_handlers.ApplicationsCLHandler),
    (r"/api/v1/cvp/applications/([^/]+)", application_handlers.ApplicationsGURHandler),

    # scenarios
    #(r"/api/v1/scenarios", scenario_handlers.ScenariosCLHandler),
    #(r"/api/v1/scenarios/([^/]+)", scenario_handlers.ScenarioGURHandler),


    #(r'/', root.RootHandler),
    (r'/api/v1/auth/signin', sign.SigninHandler),
    (r'/api/v1/auth/signin_return', sign.SigninReturnHandler),
    (r'/api/v1/auth/signin_return_jira', sign.SigninReturnJiraHandler),
    (r'/api/v1/auth/signin_return_cas', sign.SigninReturnCasHandler),
    (r'/api/v1/auth/signout', sign.SignoutHandler),
    (r'/api/v1/profile', user.ProfileHandler),

]
